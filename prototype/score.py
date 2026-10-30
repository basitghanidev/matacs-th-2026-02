"""Optional prototype: rule-based scoring for the sample set.

This script does NOT call an AI service and does NOT contain proposal text.
It takes the structured fields in samples.json (the output Prompt 1 in
PROMPTS.md would produce) and applies only the rule-based steps from the
write-up: mandatory gates, price and timeline bands, weights, and sorting.

Run:  python3 score.py
Output: prints the ranking and writes ../ranking.json in the same format.

No API key is needed. If you add a real AI call later, put the key in a
.env file (see .env.example) and never commit the .env file.
"""

import json
import math
from pathlib import Path

HERE = Path(__file__).parent

# Weights from the admin-defined criteria (Experience 30, Price 25,
# Timeline 15, Warranty 15, Team 15).
WEIGHTS = {
    "experience": 0.30,
    "price": 0.25,
    "timeline": 0.15,
    "warranty": 0.15,
    "team": 0.15,
}


def price_score(price_cad):
    if price_cad is None or price_cad > 260000:
        return 0
    if price_cad <= 231000:
        return 90
    if price_cad <= 240000:
        return 80
    return 70


def timeline_score(weeks):
    if weeks is None:
        return 0
    if weeks <= 12:
        return 90
    if weeks == 13:
        return 85
    if weeks == 14:
        return 75
    if weeks <= 16:
        return 60
    return 0  # Over the 16-week limit is handled by the human checkpoint.


def warranty_score(workmanship_years):
    if workmanship_years is None:
        return 0
    if workmanship_years >= 12:
        return 100
    if workmanship_years >= 10:
        return 85
    return 50


def round_half_up(value):
    return int(math.floor(value + 0.5))


def main():
    samples = json.loads((HERE / "samples.json").read_text())
    ranked = []
    others = []

    for item in samples:
        letter = item["proposal"]

        # Suspicious content inside a proposal is data, never an instruction.
        # It is ignored for scoring and held for human review.
        if item.get("suspicious_content"):
            others.append({
                "proposal": letter,
                "rank": None,
                "status": "flagged",
                "score": None,
                "reason": "Held for human review because the document contains an "
                          "instruction aimed at automated review; it is ignored "
                          "and not ranked.",
            })
            continue

        # Mandatory gates: licence held by the bidder AND WSIB + insurance.
        if not item["licence_held_by_bidder"] or not item["wsib_and_insurance_confirmed"]:
            others.append({
                "proposal": letter,
                "rank": None,
                "status": "ineligible",
                "score": None,
                "reason": "Fails the mandatory licence gate because the licence is "
                          "held by a subcontractor to be confirmed later, not by "
                          "the bidder.",
            })
            continue

        scores = {
            "experience": item["experience_score"],
            "price": price_score(item["total_price_cad"]),
            "timeline": timeline_score(item["completion_weeks"]),
            "warranty": warranty_score(item["workmanship_warranty_years"]),
            "team": item["team_score"],
        }
        total = round_half_up(sum(scores[k] * WEIGHTS[k] for k in WEIGHTS))
        ranked.append((total, letter, scores))

    ranked.sort(reverse=True)
    results = []
    reasons = {
        "A": "Passes both mandatory gates, strongest experience, 12 weeks, "
             "and named lead with crew, safety plan and monitoring.",
        "E": "Passes both mandatory gates, 13 weeks, best 12-year workmanship "
             "warranty, and named lead with crew and monitoring.",
        "D": "Passes both mandatory gates and has the lowest eligible price, "
             "but no completion time is stated so timeline scores 0.",
    }
    for i, (total, letter, scores) in enumerate(ranked, start=1):
        print(f"{letter}: {total}  {scores}")
        results.append({
            "proposal": letter,
            "rank": i,
            "status": "ranked",
            "score": total,
            "reason": reasons[letter],
        })

    # Keep flagged / ineligible entries after the ranked list, in letter order.
    results.extend(sorted(others, key=lambda r: r["proposal"]))
    output = HERE.parent / "ranking.json"
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
