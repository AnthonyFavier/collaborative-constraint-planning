# Larger set — Noisy radio transcripts with implied constraints

Below are **ten** longer radio exchanges. Each transcript contains normal chatter and background noise, plus **one implied operational detail** that should be interpreted later as a planning constraint. The radio lines never mention PDDL actions or planning terminology — they’re naturalistic. After each transcript I list a short **Planner interpretation** (plain-language) so it’s unambiguous which constraint to extract.

---

## Transcript A — "PLANE2 propulsion advisory (Washington)"

`09:12:03 UTC — ATC-Washington ⇢ PLANE2`

> ATC: "Plane2, this is Washington Tower. Did you receive the midnight tech brief?"

`09:12:15 UTC — PLANE2 ⇢ ATC-Washington`

> PLANE2: "We copy. Techs found a propulsion controller anomaly that causes surging when we request sustained high thrust. Cleared for service but techs recommend **keep power at or below cruise; avoid sustained high-thrust** until bench testing. Fuel steady at 1469. Over."

`09:12:28 UTC — ATC-Washington ⇢ Ops`

> ATC: "Ops, Plane2 is limited on high-power ops. See maintenance log for details."

`09:12:34 UTC — Ground-Tech ⇢ PLANE2`

> Tech: "We isolated actuator. No immediate grounding but high-thrust envelope is off limits until further notice."

`09:13:01 UTC — PLANE2 ⇢ Dispatch`

> PLANE2: "We have 8 pax manifest for next rotation. Also noted light vibration with anti-ice on. Gate change in 15."

`09:13:22 UTC — Ops ⇢ All`

> Ops: "Copy. Passenger transfers on hold pending reassign."

**Planner interpretation:**

* Constraint: **Plane2 must operate only within normal/cruise power envelope (no sustained high-thrust).** For planning, treat any legs flown by Plane2 as requiring the lower fuel-consumption profile and avoid assigning it to tasks that would need sustained high power.

---

## Transcript B — "LosAngeles fueling outage (LAX)"

`11:05:44 UTC — LA-Ground ⇢ All`

> LA Ground: "Ramp teams, all ops — hydrant contamination detected. Fuel uplift is suspended across the LAX ramp. **No fueling at LosAngeles until labs clear samples.**"

`11:06:02 UTC — PLANE3 ⇢ Ops`

> PLANE3: "Copy. Planned top at LAX before westbound leg; current fuel 1532, capacity 5204. Standing by for reassign."

`11:06:19 UTC — Ops ⇢ Dispatch`

> Ops: "Treat LAX as offline for fuel. Check alternate airports and reassign passengers if necessary. Gate congestion expected."

`11:06:45 UTC — LA Ground ⇢ PLANE5`

> LA Ground: "PLANE5, your VIPs delayed; gate 12 hydrants offline."

`11:07:02 UTC — PLANE3 ⇢ LA Ground`

> PLANE3: "Request ETA on fuel service."

`11:07:22 UTC — LA Ground ⇢ All`

> LA Ground: "No ETA. No aircraft may take on fuel at LosAngeles for now."

**Planner interpretation:**

* Constraint: **No refueling allowed at LosAngeles.** Plans must not schedule any fuel uplift at that location.

---

## Transcript C — "Boston runway weight restriction"

`07:48:10 UTC — Boston-ATC ⇢ All`

> ATC: "Attention inbound/outbound: runway 22R currently restricted to aircraft with takeoff weight under 60 tons due to pavement repairs. **Heavy departures may be limited.**"

`07:48:26 UTC — PLANE1 ⇢ Crew`

> Pilot: "Dispatch, note runway limit — if we leave heavy, may need to offload fuel or pax. Also catering delayed 25; expect pushback at 07:55."

`07:48:40 UTC — Ground ⇢ Ops`

> Ground: "We can provide limited offload. Cargo team on standby. Crosswind moderate."

`07:48:55 UTC — Ops ⇢ Dispatch`

> Ops: "Reassign heavy loads. Prefer light departure profiles for 22R until repairs complete."

**Planner interpretation:**

* Constraint: **At Boston, takeoffs requiring a heavy takeoff weight are restricted.** Practically: if an aircraft would be above a certain weight threshold (e.g., because of full fuel or too many passengers), it should not depart from Boston while the restriction is in effect — planner must ensure departures from Boston respect the weight limit by offloading passengers or fuel beforehand.

---

## Transcript D — "Seattle temporary passenger-seat removal"

`13:22:12 UTC — Seattle-Handling ⇢ All`

> Handling: "Crew, a seat-bank in Row 12 of gate-side aircraft failed the safety latch test. For any rotations leaving SEA in the next 3 hours we must **remove two cabin seats from service** on the noted tail until replacement parts arrive."

`13:22:41 UTC — PLANE3 ⇢ Ops`

> PLANE3: "Copy. That reduces our available pax seating for the next departures."

`13:23:04 UTC — Ops ⇢ Dispatch`

> Ops: "Rebalance manifests — where necessary transfer passengers to other aircraft."

`13:23:19 UTC — Passenger (PA)`

> "We apologize for seat changes. We’ll keep you updated."

**Planner interpretation:**

* Constraint: **Plane(s) operating from Seattle have reduced passenger capacity by 2 seats** for the next few rotations. Plans must not assume full passenger capacity for departures from Seattle during this window.

---

## Transcript E — "Fuel leak on PLANE1 (Boston)"

`15:02:02 UTC — PLANE1 ⇢ Ground-Tech`

> PLANE1: "Techs, cockpit reports slight fuel pressure drop after last taxi. We logged a minor fuel leak at valve B. Readout shows fuel decreasing at a rate \~0.5 units per minute during ground ops. No rapid loss but **effective usable uplift will be reduced until repair**."

`15:02:20 UTC — Ground-Tech ⇢ PLANE1`

> Tech: "We can patch but ETA 45 minutes. Recommend avoiding scheduling legs that assume full usable fuel immediately."

`15:02:48 UTC — Ops ⇢ PLANE1`

> Ops: "Copy. Consider usable fuel reduced by a safety margin."

**Planner interpretation:**

* Constraint: **Plane1 has a fuel-availability reduction due to leak — usable fuel should be treated as lower than the gauge indicates (apply a safety margin or a fixed reduction).** Plans must not assume the full available capacity for long legs until repaired.

---

## Transcript F — "Tower denies night approaches (Denver) — weather"

`20:11:11 UTC — Denver-Tower ⇢ All`

> Denver Tower: "Due to runway lighting system intermittent faults, **we will not accept night approaches** for the next 6 hours. Any arrivals after local sunset must be held or diverted."

`20:11:33 UTC — PLANE7 ⇢ Ops`

> PLANE7: "Copy Denver — holding patterns available. We’ll avoid night arrivals."

`20:11:52 UTC — Ops ⇢ Dispatch`

> Ops: "Reschedule legs to avoid Denver arrivals during night window; consider earlier departures or alternative hubs."

**Planner interpretation:**

* Constraint: **No arrivals to Denver during the night window.** Plans must avoid routing passengers to Denver with arrival times in the restricted nighttime period (this implies certain legs cannot end in Denver during that interval).

---

## Transcript G — "Crew duty limits on PLANE3"

`05:55:00 UTC — CrewOps ⇢ PLANE3`

> CrewOps: "PLANE3 crew reporting cumulative duty time near regulatory limit. If we assign another rotation beyond two more sectors, crew will exceed legal hours. **We need either a crew swap or limit Plane3 to two more sectors.**"

`05:55:18 UTC — PLANE3 ⇢ Crew`

> Pilot: "We can do two more but need relief at next scheduling point."

`05:55:43 UTC — Ops ⇢ Dispatch`

> Ops: "Plan accordingly; avoid chaining multiple legs on Plane3 without crew relief."

**Planner interpretation:**

* Constraint: **Plane3 is limited to at most two additional flight segments before a crew change is required.** Planner must not assign more than that number of legs in sequence to Plane3 without scheduling crew relief.

---

## Transcript H — "Navigation restriction over Washington-Boston corridor"

`10:30:00 UTC — ATC-Northeast ⇢ All`

> ATC: "Due to military exercise, the corridor between Washington and Boston is restricted to slow transit and must be traversed only on designated lower-altitude routes — **no high-speed dash through the corridor** for the next 4 hours."

`10:30:22 UTC — PLANE2 ⇢ ATC`

> PLANE2: "We’ll route accordingly. Expect longer transit time."

`10:30:40 UTC — Ops ⇢ All`

> Ops: "Note the corridor restriction; adjust fuel planning and sequences for affected legs."

**Planner interpretation:**

* Constraint: **Legs through the Washington–Boston corridor must use lower-speed transit profiles (i.e., plan for slower operations and higher fuel cost per distance/time).** Plans should not assume fast/high-thrust runs through that corridor during the restriction.

---

## Transcript I — "Partial fuel service at Dallas (limited uplift rate)"

`14:40:10 UTC — Dallas-Fuel ⇢ Ops`

> Dallas Fuel: "Stations at DAL are operating on limited pressure — **uplift rate capped at 40% of normal** until pumps serviced. Aircraft expecting quick top-ups will get slower service."

`14:40:32 UTC — PLANE2 ⇢ Ops`

> PLANE2: "Copy. That increases turnaround. If we need full tanks, plan for longer dwell or route to alternate."

`14:40:50 UTC — Ops ⇢ Dispatch`

> Ops: "Prioritize quick refuels for short hops; long-haul fills go to other hubs."

**Planner interpretation:**

* Constraint: **Fueling at Dallas is rate-limited (slow uplift).** Planners must account for longer turnarounds if a plan requires a full refuel at Dallas, or prefer alternative refuel locations.

---

## Transcript J — "Gate-size restriction at Washington (no large frames on Gate 3)"

`12:05:05 UTC — Washington-Ground ⇢ All`

> Ground: "Due to a jetbridge outage, Gate 3 is unavailable for aircraft with fuselage width > X. If your tail needs that gate, we cannot accommodate it — **please use alternate gates or adjust schedule.**"

`12:05:25 UTC — PLANE2 ⇢ Ops`

> PLANE2: "We typically use Gate 3 for quick turn; alternate gate will add taxi time."

`12:05:49 UTC — Ops ⇢ Dispatch`

> Ops: "Reassign gates; anticipate increased taxi and possible delay."

**Planner interpretation:**

* Constraint: **Plane2 (or other large framed aircraft) cannot use Gate 3 at Washington.** Practically this may increase taxi/delay or prevent quick turnarounds; planners should avoid plans that rely on Gate 3 for short-turn refuel/transfer operations for affected aircraft.

---

If you want, I can:

* convert these into a **JSON** mapping (raw transcript + extracted constraint label + suggested PDDL fluent/action restrictions), or
* produce **5–10 additional** transcripts with other constraint types (e.g., runway slope issues, fuel contamination percentages, ad-hoc passenger no-fly flags, emergency medical diversion) — say which you prefer and I’ll generate them.
