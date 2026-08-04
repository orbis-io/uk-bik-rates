# UK Company Car Tax (BIK) Rates, 2026/27 to 2029/30

Machine-readable UK company car tax data: appropriate percentages by fuel type and CO2, plug-in hybrid electric-range bands, the non-RDE2 diesel surcharge, and the eVED pay-per-mile rates announced at Autumn Budget 2025.

Published as JSON under the MIT licence, because there was nowhere to get this in a form a program could read.

## Why this exists

UK company car tax rates are published by HMRC as prose and PDF tables. Anyone building a calculator, a lease quoting tool, a payroll integration or a fleet TCO model ends up transcribing the same tables by hand, and hand-transcription is how rate tables acquire errors.

These files are generated directly from the tax engine behind the [OrbisIO company car tax calculator](https://orbisio.co.uk/blog/electric-company-car-bik-2026), which is unit-tested. The data and the calculator cannot drift apart.

## Files

| File | Contents |
|---|---|
| `appropriate-percentages.json` | Headline rate model: zero-emission schedule, PHEV treatment, ICE bands and caps, diesel surcharge |
| `co2-bands.json` | Appropriate percentage by tailpipe CO2, 51 g/km and above, expanded band by band |
| `phev-range-bands.json` | Plug-in hybrid sub-bands (1 to 50 g/km) by electric-only range |
| `eved.json` | eVED pay-per-mile rates from April 2028 |
| `metadata.json` | Provenance, coverage, and an explicit list of what is *not* included |

## Quick reference

**Zero-emission (battery electric) appropriate percentage**

| 2026/27 | 2027/28 | 2028/29 | 2029/30 |
|---|---|---|---|
| 4% | 5% | 7% | 9% |

**Plug-in hybrid, 1 to 50 g/km** — banded by electric-only range to 2027/28, then flattened:

| Electric range | 2026/27 | 2027/28 | 2028/29 | 2029/30 |
|---|---|---|---|---|
| 130 miles and over | 4% | 5% | 18% | 19% |
| 70 to 129 miles | 7% | 8% | 18% | 19% |
| 40 to 69 miles | 10% | 11% | 18% | 19% |
| 30 to 39 miles | 14% | 15% | 18% | 19% |
| under 30 miles | 16% | 17% | 18% | 19% |

The 2028/29 reset is the sharpest change in the schedule: a long-range PHEV goes from 5% to 18% in a single year.

**eVED, from April 2028**

| Fuel | Pence per mile |
|---|---|
| Battery electric | 3p |
| Plug-in hybrid | 1.5p |
| Petrol, diesel, conventional hybrid | not charged |

## Usage

```js
import bands from './co2-bands.json' with { type: 'json' };

function appropriatePercentage(co2, taxYear) {
  const band = bands.bands.find(
    (b) => co2 >= b.co2From && (b.co2To === null || co2 <= b.co2To)
  );
  return band?.byTaxYear[taxYear] ?? null;
}

appropriatePercentage(125, '2026/27'); // 31
```

Percentages in `co2-bands.json` are before any non-RDE2 diesel surcharge. Add 4 percentage points for a diesel not certified to RDE2, then apply the cap for that tax year (37% to 2027/28, 38% in 2028/29, 39% in 2029/30).

To get a taxable benefit, multiply the vehicle's P11D value by the appropriate percentage. The employee's income tax is that benefit at their marginal rate.

## What this does not cover

Deliberately scoped to the appropriate-percentage model. Not included:

- Income tax band thresholds, which change independently
- Employer Class 1A National Insurance
- Van benefit charge and fuel benefit charge
- Scottish and Welsh income tax variations

## Accuracy

Figures reflect HMRC appropriate-percentage policy announced to 2029/30, plus the Autumn Budget 2025 eVED measure. This is reference data, not tax advice. Verify against HMRC guidance before relying on it for a filing or a commercial quote.

Found something wrong? Open an issue. Corrections are the point of publishing this openly.

## Updates

Regenerated whenever rates change, which in practice means each Budget and any in-year rate announcement.

## Related

- [Company car tax calculator](https://orbisio.co.uk/blog/electric-company-car-bik-2026) — the calculator this data is generated from
- The Four-Year BIK Cliff — analysis of what the 2026/27 to 2029/30 schedule does to EV and PHEV costs. Analysis forthcoming; this section will link it on publication.

## Licence

MIT. Use it commercially, embed it, redistribute it. Attribution appreciated but not required.
