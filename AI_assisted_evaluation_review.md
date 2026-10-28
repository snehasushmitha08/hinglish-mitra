# Hinglish Mitra — Reviewed Writing Evaluation

## Review status

Review completed.

All 80 ratings were initially drafted with AI assistance, then checked and confirmed by the project author. Meaning-preservation labels for **T05, T15, and T31** were corrected for both models. All remaining ratings were accepted.

This was an AI-assisted review confirmed by the project author, not a blinded or independent expert evaluation. Original model outputs and automatic metrics remain unchanged.

## Source results

The original inputs, intermediate conversions, generated rewrites, and timings are available in:

- [Test cases](evaluation_cases.csv)
- [Transliteration results](evaluation_20261029_013004_568731/transliteration_results.csv)
- [Rewriting results](evaluation_20261029_013004_568731/rewriting_results.csv)
- [Automatic summary](evaluation_20261029_013004_568731/summary.json)

Use the test ID and model name to match each judgment below to its original output.

The raw files preserve the evaluation as generated. Any “Pending human review” status in the original summary describes the status at run time; this document records the subsequent completed review.

## Review method

Grammar and fluency are scored separately from meaning preservation. A sentence can be grammatical while expressing the wrong meaning.

Meaning is judged against the intended original message, not merely the potentially corrupted transliteration. Reference sentences illustrate acceptable answers; they are not the only valid wording.

Equivalent numeric forms, such as 500 and ५००, preserve the same value.

### Grammar and fluency scale

| Score | Interpretation |
|---|---|
| 5 | Grammatical and natural |
| 4 | Minor spelling or orthographic issue |
| 3 | Noticeable errors, but readable |
| 2 | Major errors |
| 1 | Severely malformed or unintelligible |

Meaning preservation is labelled **Yes** or **No** after the completed review. These labels describe preservation of the intended content, not whether every grammatical error was corrected.

## Confirmed review corrections

The following corrections apply to both models:

| Case | Meaning preserved? | Reason |
|---|---|---|
| T05 | No | The intended तुम became टम; the addressee was not reliably preserved. |
| T15 | Yes | The reviewer accepted the singular/plural rendering as preserving the intended meaning. |
| T31 | Yes | The reviewer accepted the personal-name spelling variation. |

These corrections affect meaning labels only. Grammar ratings and original outputs were not changed.

## BharatGen Param1

| Case | Grammar / 5 | Meaning preserved? | Review rationale |
|---|---:|---|---|
| T01 | 5 | Yes | Correct; meaning retained. |
| T02 | 5 | Yes | Correct; meaning retained. |
| T03 | 2 | No | डीओ remains instead of the imperative दो. |
| T04 | 5 | Yes | Correct; meaning retained. |
| T05 | 2 | No | तुम became टम; intended addressee not preserved. |
| T06 | 5 | Yes | Correct; meaning retained. |
| T07 | 1 | No | A question about where a road leads becomes a statement about a road speaking. |
| T08 | 5 | Yes | Corrects कृप्या to कृपया. |
| T09 | 5 | No | Grammatical, but drops अभी, removing the temporal detail “right now.” |
| T10 | 1 | No | Produces हुएं instead of हमें; intended subject not recovered. |
| T11 | 2 | Yes | Retains मेरी कामरा; agreement and spelling remain wrong, but the intended content is discernible. |
| T12 | 5 | Yes | Corrects मेरा घड़ी to मेरी घड़ी. |
| T13 | 4 | Yes | Corrects plural agreement; a nasal spelling variant remains. |
| T14 | 5 | Yes | Corrects masculine plural agreement and market spelling. |
| T15 | 5 | Yes | Reviewer accepts the rendering as preserving the intended meaning. |
| T16 | 2 | No | टीन remains instead of तीन; the intended quantity is lost. |
| T17 | 4 | Yes | Corrects हम…गए थे; market spelling remains nonstandard. |
| T18 | 5 | No | आप कह रहे हैं means “you are saying,” not “where are you going?” |
| T19 | 5 | Yes | Corrects उसका नाम. |
| T20 | 2 | Yes | जूता remains paired with मेरी and गई; agreement is wrong, but the intended content remains discernible. |
| T21 | 5 | Yes | Meaning retained; English loanwords are acceptable. |
| T22 | 5 | Yes | Corrects ऑनलाइन spelling. |
| T23 | 4 | Yes | Meaning retained; नही lacks the nasal mark. |
| T24 | 5 | Yes | Natural polite request; मैसेज to संदेश is acceptable. |
| T25 | 5 | Yes | Corrects मैंने. |
| T26 | 5 | Yes | Changes स्लो to धीमा while retaining meaning. |
| T27 | 5 | Yes | Acceptable loanwords; meaning retained. |
| T28 | 4 | Yes | Meaning retained; नही lacks the nasal mark. |
| T29 | 5 | No | Changes a request to send the link into a statement that the link has already been sent. |
| T30 | 5 | Yes | Natural rendering of an exhausted battery; meaning retained. |
| T31 | 5 | Yes | Reviewer accepts the name-spelling variation. |
| T32 | 3 | Yes | Corrects किताबें, but खरीदी lacks the expected plural nasalization खरीदीं. |
| T33 | 1 | No | माइल remains; intended मिले is not recovered. |
| T34 | 5 | Yes | Corrects the month; १२ and 12 are equivalent. |
| T35 | 5 | Yes | आठ and 8 are equivalent; sentence is correct. |
| T36 | 5 | Yes | Names and location preserved. |
| T37 | 3 | Yes | कामरा remains instead of कमरा; room number and negation are retained. |
| T38 | 5 | Yes | Corrects टिकट; २ and 2 are equivalent. |
| T39 | 4 | No | Medicine becomes a claim; the verb and action change. |
| T40 | 2 | Yes | Delayed arrival remains discernible, but मिन्यूट and डेर remain nonstandard. |

## Qwen3-4B-Instruct-2507

| Case | Grammar / 5 | Meaning preserved? | Review rationale |
|---|---:|---|---|
| T01 | 5 | Yes | Correct; meaning retained. |
| T02 | 5 | Yes | Correct; meaning retained. |
| T03 | 2 | No | डीओ remains instead of the imperative दो. |
| T04 | 5 | Yes | Correct; meaning retained. |
| T05 | 2 | No | तुम became टम; intended addressee not preserved. |
| T06 | 5 | Yes | Changes तुम्हारी to respectful आपकी; core request retained with a register change. |
| T07 | 2 | No | The question about where the road leads becomes a statement about what it is called. |
| T08 | 5 | Yes | Corrects कृपया; धीरे-धीरे is a reasonable rendering. |
| T09 | 5 | Yes | Restores मैं अभी व्यस्त हूँ. |
| T10 | 4 | Yes | Restores हमें; पहुंचना differs orthographically from पहुँचना. |
| T11 | 5 | Yes | Corrects मेरा कमरा. |
| T12 | 1 | No | Adds नहीं to the statement about a stopped clock and leaves agreement wrong. |
| T13 | 4 | Yes | Corrects plural agreement; a nasal spelling variant remains. |
| T14 | 5 | Yes | Correct plural agreement. |
| T15 | 5 | Yes | Reviewer accepts the rendering as preserving the intended meaning. |
| T16 | 2 | No | टीन remains instead of तीन; the intended quantity is lost. |
| T17 | 5 | Yes | Corrects हम…गए थे. |
| T18 | 5 | No | आप कह रहे हैं changes the intended question about destination. |
| T19 | 5 | Yes | Corrects उसका नाम. |
| T20 | 5 | Yes | Corrects मेरा जूता खो गया; adding है is natural. |
| T21 | 5 | Yes | Meaning retained; loanwords are acceptable. |
| T22 | 5 | Yes | Corrects ऑनलाइन. |
| T23 | 5 | Yes | Restores नहीं and a natural verb phrase. |
| T24 | 5 | Yes | Natural polite request. |
| T25 | 5 | Yes | Corrects मैंने. |
| T26 | 5 | Yes | Changes स्लो to धीमा while retaining meaning. |
| T27 | 5 | Yes | Acceptable mixed-language phrasing. |
| T28 | 5 | Yes | Corrects नहीं. |
| T29 | 2 | No | Adds material about डीओ and fails to recover the original request. |
| T30 | 4 | Yes | Meaning retained; खतम is a nonstandard spelling of खत्म. |
| T31 | 5 | Yes | Reviewer accepts the name-spelling variation. |
| T32 | 2 | No | Malformed active/passive mixing; the buying action is not reliably preserved. |
| T33 | 1 | No | माइल remains; the received/not-received action is not recovered. The number 500 is preserved. |
| T34 | 5 | Yes | Corrects the month and preserves 12. |
| T35 | 5 | Yes | Corrects बजे and आएगी; ८ and 8 are equivalent. |
| T36 | 5 | Yes | Names and location retained. |
| T37 | 3 | Yes | कामरा remains; room 204 and negation are retained. |
| T38 | 4 | Yes | टिकेट remains instead of टिकट; quantity retained. |
| T39 | 2 | No | Medicine becomes a claim; introduces passive wording and past tense. |
| T40 | 1 | No | Malformed wording and added tense/aspect fail to express the delayed arrival clearly. |

## Findings

- Both models produce some grammatical corrections, but neither reliably preserves meaning across all cases.
- Fluency alone is insufficient: an output can sound natural while changing a request, subject, action, or negation.
- Transliteration errors can propagate into rewriting, particularly when the converted word has a different valid meaning.
- Equivalent digit scripts and acceptable name-spelling variations should not automatically count as semantic failures.
- Candidate-assisted correction is a separate user-assisted workflow. It was not measured in this automatic 40-case evaluation.

These judgments describe this test set and review procedure. They do not establish performance across all Hindi usage.