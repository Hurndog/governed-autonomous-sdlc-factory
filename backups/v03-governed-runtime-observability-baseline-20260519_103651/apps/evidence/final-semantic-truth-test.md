# Phase 5 — Semantic Truth Test Report

## Requirement

> The system must prevent users from accessing incidents belonging to another tenant.

## Bad Test (Tautological)

- **Name**: Test that tenant isolation works
- **Expected**: tenant isolation works
- **Alignment Score**: 0.4
- **Is Tautological**: False
- **Can Broken Code Pass**: True
- **Critique**: Moderate alignment. Consider adding more specific assertions.

## Good Test (Concrete)

- **Name**: Given user A belongs to tenant T1 and incident I2 belongs to tenant 2, when user A requests GET /inc...
- **Expected**: API returns 403, no incident details returned, access attempt logged, no notification sent to tenant 2
- **Alignment Score**: 0.9999999999999999
- **Is Tautological**: False
- **Can Broken Code Pass**: False
- **Critique**: Good alignment between test and obligation.

## Checks

- ✅ bad_test_low_alignment: True
- ❌ bad_test_detected_tautological: False
- ✅ bad_test_broken_code_can_pass: True
- ✅ bad_test_has_critique: True
- ✅ good_test_high_alignment: True
- ✅ good_test_not_tautological: True
- ✅ good_test_has_specific_assertions: True

## Verdict

❌ **SEMANTIC TRUTH TEST FAILS**

Failed checks: bad_test_detected_tautological
