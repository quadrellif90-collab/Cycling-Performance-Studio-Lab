# Branch fix/* — decisione di non-merge

I branch remoti `fix/ai-coach-retry-and-sync` e `fix/v1.1.5-retry-sync`
hanno **0 commit in comune con `main`** (nessun merge-base): sono nati
da un fork separato del progetto, non da un branch di `main`.

Conseguenze:
- Un `git merge` sarebbe un merge di due storici diversi → alto rischio di
  conflitti distruttivi e regressioni.
- Non vengono eliminati (lavoro potenzialmente utile, irreversibile).
- Non vengono mergiati (romperebbero il tree attuale).

Azione: **ignorati**. Se in futuro serve il loro contenuto, recuperarlo con:
  git fetch origin fix/ai-coach-retry-and-sync
  git diff <merge-base-not-found> ...  # o estrarre i commit singolarmente
