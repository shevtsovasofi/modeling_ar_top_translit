# Project rendering profile

This is a simplified project convention, not a claimed implementation of UNGEGN or another formal national standard.

- Arabic NFC and whitespace normalization; a separate matching key removes tatweel and diacritics. Base letter variants are not merged by rendering.
- Longest initial whole-token generic phrase is preferred. Proper names are transliterated; confirmed generic terms are translated and placed using explicit templates.
- Orthographic article: Al / Аль with a space. Assimilation is available only under a separate explicit phonetic option. Article-related shadda is not duplicated in the orthographic stem.
- English suffix templates: Street, Road, Highway, Bridge, Airport, Park, University, Valley, Island. Mount and Lake precede the proper name. Other confirmed generic terms require a template rather than an inferred English word order.
- Russian generic terms precede the name. General case inflection is not implemented. Generic-plus-title candidates receive russian_inflection_required rather than being accepted as fully processed.
- Long vowels are recorded in traces but displayed without macrons. Short vowels, sukun, shadda, hamza, madda, and explicit diphthongs are handled separately.
- Ta marbuta uses a pause-form a/а with an idafa warning. Idafa detection and a general morphology module are absent.
- A missing mark on a terminal consonant does not alone trigger incomplete_diacritization. Missing internal marks can trigger it. This is a display heuristic, not proof of a unique pronunciation.
- Uncertain generic roles remain untranslated and are flagged. The component زهرة is not automatically translated as a generic term.
- A scoped verified exception may override generated text. Do not supply test reference labels as exceptions when evaluating automatic generation.
- Changed base letters cause rejection. Given input marks are preserved. The default model scope is full-name diacritization, matching the training representation; proper-only mode requires a separate evaluation.

See the executable tables and tests for the precise implemented mappings. Control examples test logic and do not establish linguistic accuracy on real objects.
