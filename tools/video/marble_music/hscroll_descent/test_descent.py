"""Timing, clearance, surface, energy, and the separate rail transition.

Run from tools/video/marble_music:

    python -m unittest hscroll_descent.test_descent hscroll_descent.test_rail -v
"""

import copy
import json
import os
import unittest

import numpy as np

from hscroll_descent.audit import audit_route
from hscroll_descent.physics import classify_bounce, reflect
from hscroll_descent.plan import plan_document, plan_hits
from hscroll_descent.rail import audit_transition, plan_guided_hop, refusal_if_lip_too_high, static_deflector

HERE = os.path.dirname(os.path.abspath(__file__))
HITS = os.path.join(HERE, "examples", "jingle_remix_0_9_melody.hits.json")


def _excerpt():
    with open(HITS, encoding="utf-8") as handle:
        document = json.load(handle)
    return plan_document(
        document, g=9.81, seed=2, fps=30, tilt_deg=60.0, long_note=0.60,
        patterns="fold,fold,compact,shuttle", plate_half=0.15,
    )


class DescentExcerpt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = _excerpt()

    def test_excerpt_is_passive_and_timed(self):
        self.assertEqual(self.route["status"], "ok", self.route.get("message"))
        report = audit_route(self.route)
        self.assertTrue(report["ok"], report["violations"][:5])
        self.assertLessEqual(report["summary"]["max_energy_gain_j_per_kg"], 1e-7)
        self.assertGreater(report["summary"]["min_proxy_clearance_m"], 0.012)
        self.assertEqual(report["summary"]["full_triangle_mesh"], "not run")
        self.assertEqual(report["summary"]["probe_point_keepout_pairs"], "not run")
        self.assertIn("excerpt", report["summary"]["scope"])
        times = [hit["time"] for hit in self.route["hits"]]
        for contact, midi_t in zip(self.route["contacts"], times):
            self.assertAlmostEqual(contact["time"], midi_t, places=9)
        zs = [contact["p"][1] for contact in self.route["contacts"]]
        self.assertLess(zs[-1], zs[0] - 0.5)
        layers = []
        for contact in self.route["contacts"]:
            if not layers or layers[-1][0] != contact["layer"]:
                layers.append((contact["layer"], contact["p"][1]))
        for (prev, _z), (nxt, z) in zip(layers, layers[1:]):
            self.assertGreater(nxt, prev)
            previous_floor = min(c["p"][1] for c in self.route["contacts"] if c["layer"] == prev)
            self.assertLess(z, previous_floor)

    def test_local_lob_is_allowed_when_kinetic_energy_pays(self):
        # A long note may leave upward and still land lower. That is a lob, not a height reset.
        climbed = False
        for flight in self.route["flights"]:
            if flight["role"] != "hop":
                continue
            vz = flight["v"][1]
            if vz <= 0:
                continue
            g = self.route["g"]
            dt = flight["t1"] - flight["t0"]
            apex = flight["p0"][1] + vz * vz / (2 * g)
            end_z = flight["p0"][1] + vz * dt - 0.5 * g * dt * dt
            if apex > flight["p0"][1] + 0.05 and end_z < flight["p0"][1]:
                climbed = True
                break
        self.assertTrue(climbed)

    def test_negative_energy_injection_is_rejected(self):
        vin = np.array([0.4, -2.2])
        normal = np.array([0.0, 1.0])
        injected = reflect(vin, normal, 1.45)
        verdict = classify_bounce(vin, injected, normal)
        self.assertFalse(verdict["ok"])
        self.assertEqual(verdict["reason"], "energy_injection")
        self.assertGreater(verdict["energy_gain"], 0.0)
        mutated = copy.deepcopy(self.route)
        contact = mutated["contacts"][1]
        contact["vout"] = reflect(np.array(contact["vin"]), np.array(contact["normal"]), 1.4).tolist()
        report = audit_route(mutated)
        self.assertFalse(report["ok"])
        self.assertTrue(any(item["reason"] == "energy_injection" for item in report["violations"]))

    def test_impossible_gap_reports_deficit_without_relaxing(self):
        hits = [
            dict(time=0.0, note=60, track_name="t", drum=False),
            dict(time=1.2, note=62, track_name="t", drum=False),
        ]
        refused = plan_hits(
            hits, g=9.81, seed=1, entry_vin=(0.3, -0.9), max_drop=0.25, duration=1.7,
        )
        self.assertEqual(refused["status"], "impossible")
        self.assertFalse(refused["energy_was_relaxed"])
        self.assertGreater(refused["energy_deficit_j_per_kg"], 0.0)
        self.assertTrue(refused["tradeoffs"])
        self.assertNotIn("keys", refused)


class RailTransition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The 1.22449 s gap is the long note in the checked-in Jingle Bells remix.
        cls.result = plan_guided_hop(np.array([2.35, 0.85]), 1.22449)

    def test_fall_then_leftward_rail_then_lower_strike(self):
        self.assertEqual(self.result["status"], "ok", self.result.get("message"))
        self.assertFalse(self.result["renderer_supported"])
        self.assertFalse(self.result["powered_kicker"])
        self.assertTrue(self.result["audit"]["ok"], self.result["audit"])
        fall, slip, rail, launch = self.result["phases"]
        self.assertGreater(self.result["speed_at_capture"], self.result["speed_at_launch"] + 0.2)
        self.assertGreater(slip["energy_loss_j_per_kg"], 0.0)
        self.assertGreater(rail["z_exit"], rail["z_valley"] + 0.04)
        self.assertLess(rail["z_exit"], rail["z_entry"])
        self.assertLess(rail["v_exit"][0], -0.15)
        self.assertLess(self.result["landing"]["p"][1], -0.25)
        self.assertLess(self.result["landing"]["v"][1], -0.2)
        total = sum(phase["duration_s"] for phase in self.result["phases"])
        self.assertAlmostEqual(total, 1.22449, places=3)
        # Samples on the lip climb. Descent is not required at every sample.
        zs = [row["z"] for row in rail["samples"]]
        self.assertGreater(zs[-1], min(zs))
        self.assertEqual(rail["force"], "constraint_normal_and_static_friction")
        self.assertEqual(slip["force"], "kinetic_friction_over_a_finite_slip")

    def test_channel_is_the_path_and_not_a_flat_ribbon(self):
        from hscroll_descent.rail_geometry import build_channel
        guide = self.result
        channel = build_channel(guide)
        for station in channel["stations"]:
            dx = station["floor"][0] - station["center"][0]
            dz = station["floor"][2] - station["center"][2]
            self.assertAlmostEqual((dx * dx + dz * dz) ** 0.5, 0.15, places=2)
        self.assertGreater(max(s["outer_h"] for s in channel["stations"]),
                           max(s["inner_h"] for s in channel["stations"]) + 0.04)
        self.assertLess(channel["stations"][-1]["outer_h"], 0.03)
        zs = [s["center"][2] for s in channel["stations"]]
        self.assertGreater(zs[-1], min(zs) + 0.02)

    def test_injected_exit_speed_is_not_passive(self):
        tampered = copy.deepcopy(self.result)
        rail = tampered["phases"][2]
        rail["v_exit"] = [component * 1.25 for component in rail["v_exit"]]
        rail["v_end"] = rail["v_exit"]
        report = audit_transition(tampered)
        self.assertFalse(report["ok"])

    def test_lip_above_the_budget_does_not_add_a_kicker(self):
        refused = refusal_if_lip_too_high()
        self.assertEqual(refused["status"], "cannot_crest_lip")
        self.assertFalse(refused["powered_kicker"])
        self.assertGreater(refused["energy_deficit_j_per_kg"], 0.0)

    def test_static_deflector_is_an_impulse_not_a_spring(self):
        vin = np.array([2.0, -1.0])
        normal = np.array([-0.6, 0.8])
        normal = normal / np.linalg.norm(normal)
        kept = static_deflector(vin, normal, 0.8)
        self.assertTrue(kept["ok"])
        self.assertFalse(kept["powered_kicker"])
        self.assertEqual(kept["kind"], "impact_impulse")
        kicked = static_deflector(vin, normal, 1.5)
        self.assertFalse(kicked["ok"])
        self.assertTrue(kicked["powered_kicker"])


if __name__ == "__main__":
    unittest.main()
