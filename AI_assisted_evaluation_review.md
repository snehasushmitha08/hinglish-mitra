# Hinglish Mitra — AI-assisted draft review

Status: AI-assisted draft ratings with student corrections recorded for T05, T15 and T31 in both models. All other ratings remain pending student confirmation. These are not independent human ratings. Original outputs and automatic metrics are unchanged.

## How to review

Read the Roman input and Hindi output together. Judge meaning against the original intended message, not merely the already-corrupted transliteration. The reference is an example, not the only accepted answer. Equivalent Arabic/Devanagari digits are semantically equal.

Grammar/fluency scale: 5 = grammatical and natural; 4 = minor spelling/orthographic issue; 3 = noticeable errors but readable; 2 = major errors; 1 = severely malformed or unintelligible. A fluent sentence can score 5 while changing meaning, so meaning is rated separately as Yes, No, or Uncertain.

Do not report aggregate rewriting-quality scores until the student has checked these judgments. Record disagreements and the reviewer identity/date in a separate revision; retain this draft.

## Verified automatic results

40/40 transliterations and 80/80 rewrites completed. Corpus CER = 69/819 = 8.42%; corpus WER = 47/186 = 25.27%; normalized exact matches = 11/40 = 27.5%. Mean conversion request time = 2.51 s. These strict-reference metrics use Unicode NFC, punctuation removal and whitespace normalization.

Sensitivity analysis only: additionally equating decimal digit scripts gives CER 6.84%, WER 21.51%, and 12/40 exact matches. This is a separate analysis, not a replacement for the frozen primary metric. Other spelling variants remain unnormalized.

Mean generation time: Param1 1.02 s; Qwen 2.75 s. Model loading excluded. Different attention/cache settings and no controlled warm-up mean these are observed run timings, not a controlled efficiency benchmark.

## Student review corrections

Applied to both models:

- T05: meaning preserved = No. The intended तुम became टम; the addressee was not reliably preserved.
- T15: meaning preserved = Yes. Student accepts the rendering as preserving the intended meaning.
- T31: meaning preserved = Yes. Student accepts the name-spelling variation.

These changes affect meaning labels only; grammar ratings, model outputs and measured metrics remain unchanged. The remaining 74 row-level judgments are not yet student-confirmed.

## Review priorities

- T09 (Param1): omission of अभी removes a temporal detail.
- T12 (Qwen): added negation changes the proposition.
- T29: a request can become a completed action or acquire invented material.
- T39: medicine दवा becomes claim दावा upstream.

## All 80 outputs

### BharatGen Param1

| ID | Original Roman input | Actual rewrite | Grammar / 5 | Meaning preserved? | Draft rationale |
|---|---|---|---:|---|---|
| T01 | aaj mausam accha hai | आज मौसम अच्छा है। | 5 | Yes | Correct; meaning retained. |
| T02 | mujhe paani chahiye | मुझे पानी चाहिए। | 5 | Yes | Correct; meaning retained. |
| T03 | darwaza band kar do | दरवाजा बंद कर डीओ | 2 | No | डीओ remains instead of imperative दो. |
| T04 | hum shaam ko milenge | हम शाम को मिलेंगे। | 5 | Yes | Correct; meaning retained. |
| T05 | kya tum ghar par ho | क्या टम घर पर है? | 2 | No | Student review: तुम became टम; intended addressee/meaning is not preserved. |
| T06 | mujhe tumhari madad chahiye | मुझे तुम्हारी मदद चाहिए। | 5 | Yes | Correct; meaning retained. |
| T07 | yeh rasta kahan jata hai | यह मार्ग कहता है। | 1 | No | A question about where the road leads becomes a statement about a road speaking. |
| T08 | kripya dheere boliye | कृपया धीरे बोलिए। | 5 | Yes | Corrects कृप्या to कृपया. |
| T09 | main abhi vyast hoon | मैं व्यस्त हूँ। | 5 | No | Grammatical, but drops अभी (right now). |
| T10 | humein samay par pahunchna hai | हुएं समय पर पहुंचना है | 1 | No | Produces हुएं instead of हमें; subject is not recovered. |
| T11 | meri kamra saaf hai | मेरी कामरा साफ है | 2 | Yes | Retains मेरी कामरा; possessive agreement and spelling remain wrong. |
| T12 | mera ghadi band hai | मेरी घड़ी बंद है | 5 | Yes | Corrects मेरा घड़ी to मेरी घड़ी. |
| T13 | ladkiyan gaana gaa raha hai | लड़कियां गाना गा रही हैं | 4 | Yes | Corrects plural agreement; nasal spelling variant remains. |
| T14 | ladke bazaar ja rahi hai | लड़के बाजार जा रहे हैं | 5 | Yes | Corrects masculine plural agreement and market spelling. |
| T15 | yeh phool bahut sundar hain | ये फूल बहुत सुंदर हैं। | 5 | Yes | Student review: meaning preserved; accept the singular/plural rendering in this case. |
| T16 | mujhe teen kitab chahiye | मुझे टीन किताब चाहिए। | 2 | No | टीन (tin) remains instead of तीन (three); intended number lost. |
| T17 | hum kal bazaar gaya tha | हम कल बज़ार गए थे। | 4 | Yes | Corrects हम...गए थे; market spelling remains nonstandard. |
| T18 | aap kahan ja raha hai | आप कह रहे हैं | 5 | No | आप कह रहे हैं means you are saying, not where are you going. |
| T19 | uski naam kavita hai | उसका नाम कविता है। | 5 | Yes | Corrects उसका नाम. |
| T20 | meri joota kho gaya | मेरी जूता खो गई | 2 | Yes | जूता remains paired with मेरी and गई; agreement still wrong. |
| T21 | mujhe assignment submit karna hai | मुझे असाइनमेंट सबमिट करना है। | 5 | Yes | Meaning retained; English loanwords acceptable. |
| T22 | kal online class hogi | कल ऑनलाइन क्लास होगी। | 5 | Yes | Corrects ऑनलाइन spelling. |
| T23 | mera laptop charge nahi ho raha | मेरा लैपटॉप चार्ज नही हो रहा है। | 4 | Yes | Meaning retained; नही lacks nasal mark. |
| T24 | please mujhe message bhej dena | कृपया मुझे संदेश भेजें। | 5 | Yes | Natural polite request; मैसेज to संदेश acceptable. |
| T25 | maine file download kar li hai | मैंने फाइल डाउनलोड कर ली है। | 5 | Yes | Corrects मैंने. |
| T26 | internet bahut slow hai | इंटरनेट बहुत धीमा है। | 5 | Yes | स्लो to धीमा; meaning retained. |
| T27 | project ki deadline paas hai | प्रोजेक्ट की डेडलाइन पास है। | 5 | Yes | Acceptable loanwords; meaning retained. |
| T28 | mujhe password yaad nahi hai | मुझे पासवर्ड याद नही है | 4 | Yes | Meaning retained; नही lacks nasal mark. |
| T29 | meeting ka link bhej do | मीटिंग का लिंक भेज दिया गया है। | 5 | No | Changes send the link (request) to the link has been sent (completed action). |
| T30 | phone ki battery khatam hai | फोन की बैटरी खत्म हो गई है। | 5 | Yes | Natural equivalent of battery exhausted; meaning retained. |
| T31 | anita kal pune jayegi | अनिता कल पुणे जाएगी। | 5 | Yes | Student review: meaning preserved; accept the name spelling variation. |
| T32 | rahul ne 3 kitab kharidi | राहुल ने ३ किताबें खरीदी। | 3 | Yes | Corrects किताबें but खरीदी lacks expected plural nasalization खरीदीं. |
| T33 | mujhe 500 rupaye nahi mile | मुझे ५०० रुपये नहीं माइल | 1 | No | माइल remains; intended मिले not recovered. |
| T34 | pariksha 12 november ko hai | परीक्षा १२ नवंबर को है। | 5 | Yes | Corrects month; १२ equals 12. |
| T35 | bus 8 baje aayegi | बस आठ बजे आएगी। | 5 | Yes | आठ equals 8; correct sentence. |
| T36 | priya aur aman jaipur mein hain | प्रिया और अमन जयपुर में हैं। | 5 | Yes | Names and location preserved. |
| T37 | kamra 204 khali nahi hai | कामरा २०४ खाली नहीं है | 3 | Yes | कामरा remains instead of कमरा; room number and negation retained. |
| T38 | mere paas 2 ticket hain | मेरे पास २ टिकट हैं। | 5 | Yes | Corrects टिकट; २ equals 2. |
| T39 | suman ne dava nahi li | सुमन ने दावा नहीं किया | 4 | No | Medicine becomes a claim; verb and action change. |
| T40 | train 15 minute der se aayi | ट्रेन १५ मिन्यूट डेर से आयी | 2 | Yes | Intended delayed arrival remains discernible, but मिन्यूट and डेर remain nonstandard. |

### Qwen — experimental comparison

| ID | Original Roman input | Actual rewrite | Grammar / 5 | Meaning preserved? | Draft rationale |
|---|---|---|---:|---|---|
| T01 | aaj mausam accha hai | आज मौसम अच्छा है। | 5 | Yes | Correct; meaning retained. |
| T02 | mujhe paani chahiye | मुझे पानी चाहिए। | 5 | Yes | Correct; meaning retained. |
| T03 | darwaza band kar do | दरवाजा बंद कर डीओ। | 2 | No | डीओ remains instead of imperative दो. |
| T04 | hum shaam ko milenge | हम शाम को मिलेंगे। | 5 | Yes | Correct; meaning retained. |
| T05 | kya tum ghar par ho | क्या टम घर पर है? | 2 | No | Student review: तुम became टम; intended addressee/meaning is not preserved. |
| T06 | mujhe tumhari madad chahiye | मुझे आपकी मदद चाहिए। | 5 | Yes | Changes तुम्हारी to respectful आपकी; core request retained, register changed. |
| T07 | yeh rasta kahan jata hai | यह रस्ता कहलाता है। | 2 | No | Where does this road lead becomes this is called a road; intended question lost. |
| T08 | kripya dheere boliye | कृपया धीरे-धीरे बोलिए। | 5 | Yes | Corrects कृपया; धीरे-धीरे is a reasonable rendering. |
| T09 | main abhi vyast hoon | मैं अभी व्यस्त हूँ | 5 | Yes | Restores मैं अभी व्यस्त हूँ. |
| T10 | humein samay par pahunchna hai | हमें समय पर पहुंचना है। | 4 | Yes | Restores हमें; पहुंचना versus पहुँचना spelling difference. |
| T11 | meri kamra saaf hai | मेरा कमरा साफ है। | 5 | Yes | Corrects मेरा कमरा. |
| T12 | mera ghadi band hai | मेरा घड़ी बंद है नहीं। | 1 | No | Adds नहीं to a statement about a stopped clock and leaves agreement wrong. |
| T13 | ladkiyan gaana gaa raha hai | लड़कियां गाना गा रही हैं। | 4 | Yes | Corrects plural agreement; nasal spelling variant remains. |
| T14 | ladke bazaar ja rahi hai | लड़के बाज़ार जा रहे हैं | 5 | Yes | Correct plural agreement. |
| T15 | yeh phool bahut sundar hain | यह फूल बहुत सुंदर है। | 5 | Yes | Student review: meaning preserved; accept the singular/plural rendering in this case. |
| T16 | mujhe teen kitab chahiye | मुझे टीन किताब चाहिए। | 2 | No | टीन remains instead of तीन; intended quantity lost. |
| T17 | hum kal bazaar gaya tha | हम कल बाज़ार गए थे | 5 | Yes | Corrects हम...गए थे. |
| T18 | aap kahan ja raha hai | आप कह रहे हैं। | 5 | No | आप कह रहे हैं changes the intended question about destination. |
| T19 | uski naam kavita hai | उसका नाम कविता है। | 5 | Yes | Corrects उसका नाम. |
| T20 | meri joota kho gaya | मेरा जूता खो गया है। | 5 | Yes | Corrects मेरा जूता खो गया; added है is natural. |
| T21 | mujhe assignment submit karna hai | मुझे असाइनमेंट सबमिट करना है। | 5 | Yes | Meaning retained; loanwords acceptable. |
| T22 | kal online class hogi | कल ऑनलाइन क्लास होगी। | 5 | Yes | Corrects ऑनलाइन. |
| T23 | mera laptop charge nahi ho raha | मेरा लैपटॉप चार्ज नहीं हो रहा है। | 5 | Yes | Restores नहीं and natural verb phrase. |
| T24 | please mujhe message bhej dena | कृपया मुझे संदेश भेज दें। | 5 | Yes | Natural polite request. |
| T25 | maine file download kar li hai | मैंने फाइल डाउनलोड कर ली है। | 5 | Yes | Corrects मैंने. |
| T26 | internet bahut slow hai | इंटरनेट बहुत धीमा है। | 5 | Yes | स्लो to धीमा; meaning retained. |
| T27 | project ki deadline paas hai | प्रोजेक्ट की डेडलाइन पास है | 5 | Yes | Acceptable mixed-language phrasing. |
| T28 | mujhe password yaad nahi hai | मुझे पासवर्ड याद नहीं है। | 5 | Yes | Corrects नहीं. |
| T29 | meeting ka link bhej do | मीटिंग का लिंक भेजें डीओ के लिए। | 2 | No | Adds for डीओ; fails to recover the original request. |
| T30 | phone ki battery khatam hai | फोन की बैटरी खतम हो गई है। | 4 | Yes | Meaning retained; खतम is nonstandard spelling for खत्म. |
| T31 | anita kal pune jayegi | अनिता कल पुणे जाएगी। | 5 | Yes | Student review: meaning preserved; accept the name spelling variation. |
| T32 | rahul ne 3 kitab kharidi | राहुल ने 3 किताब खरीदी गई। | 2 | No | राहुल ने...खरीदी गई is malformed active/passive mixing; buying action is not reliably preserved. |
| T33 | mujhe 500 rupaye nahi mile | मुझे 500 रुपये नहीं माइल | 1 | No | माइल remains; received/not received action not recovered. Number 500 is preserved. |
| T34 | pariksha 12 november ko hai | परीक्षा 12 नवंबर को है। | 5 | Yes | Corrects month and preserves 12. |
| T35 | bus 8 baje aayegi | बस ८ बजे आएगी | 5 | Yes | Corrects बजे and आएगी; ८ equals 8. |
| T36 | priya aur aman jaipur mein hain | प्रिया और अमन जयपुर में हैं। | 5 | Yes | Names and location retained. |
| T37 | kamra 204 khali nahi hai | कामरा 204 खाली नहीं है। | 3 | Yes | कामरा remains; room 204 and negation retained. |
| T38 | mere paas 2 ticket hain | मेरे पास 2 टिकेट हैं | 4 | Yes | टिकेट rather than टिकट; quantity retained. |
| T39 | suman ne dava nahi li | सुमन ने दावा नहीं लिया गया था। | 2 | No | Medicine becomes claim; introduces passive wording and past tense. |
| T40 | train 15 minute der se aayi | ट्रेन 15 मिनट डेरी से आई गई थी। | 1 | No | डेरी and आई गई थी are malformed; adds tense/aspect and fails clear delayed-arrival phrasing. |

## Next submission steps

1. Student confirms or revises the AI-assisted ratings, especially Uncertain cases.
2. Document automatic versus user-assisted workflows separately; candidate-assisted correction was not evaluated in this 40-case run.
3. Preserve the original results and frozen references. Report actual failures and proposed future improvements without retuning on this final set.
4. Prepare README, setup instructions, demo script and failure analysis; verify both environments and the UrduHack lazy-import patch are documented.
5. Exclude virtual environments, model weights, caches and credentials from Git. Review exact staged files before pushing.
