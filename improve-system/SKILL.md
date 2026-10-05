---
name: improve-system
description: Analyse l'historique des sessions Claude Code (~/.claude/projects/*.jsonl) et sort un rapport — erreurs répétées de Claude, demandes refaites à la main qui méritent un skill ou un script, règles à ajouter aux CLAUDE.md / mémoire. Utiliser quand l'utilisateur dit « improve system », « améliore mon système », « analyse mes sessions ».
---

# /improve-system — le système qui s'améliore tout seul

100 % local : rien ne sort de la machine. Rapport = propositions ; on n'applique qu'après accord de l'utilisateur
(sauf s'il dit « applique tout »).

## 1. Digest

```
python ~/.claude/skills/improve-system/digest.py           # depuis le dernier passage (7 jours la première fois)
python ~/.claude/skills/improve-system/digest.py --days 30 # si l'utilisateur précise une période
```

Lire `~/.claude/improve-system/digest.md` en entier (un seul Read). Ne JAMAIS lire les .jsonl bruts.
0 session → écrire « rien de neuf » et s'arrêter.

## 2. Contexte existant (pour ne pas proposer ce qui existe déjà)

- `~/.claude/CLAUDE.md` et les CLAUDE.md des projets qui apparaissent dans le digest (recherche ciblée).
- Mémoire : `~/.claude/projects/*/memory/MEMORY.md` s'il y en a.
- Liste des skills : `~/.claude/skills` et `.claude/skills` des projets concernés.
- Rapports précédents : `~/.claude/improve-system/rapports/` (ne pas reproposer une reco déjà refusée ou faite).

## 3. Analyse — chercher des MOTIFS (au moins 2 occurrences), pas des anecdotes

1. **Ce que Claude rate** : corrections répétées, mêmes erreurs d'outils, consignes déjà écrites mais pas suivies
   (→ la reformuler / la remonter, pas la dupliquer).
2. **Skills à créer** : demandes retapées avec les mêmes étapes, workflows multi-étapes refaits à la main.
3. **Automatisations** : tâches longues et répétitives (script, tâche planifiée…) avec le gain de temps estimé
   à partir des sessions (durée, nombre de relances) — jamais de chiffre inventé.
4. **Ménage** : skills jamais lancés, règles contradictoires entre CLAUDE.md, mémoires périmées.
5. **Pour l'utilisateur** : habitudes qui lui coûtent du temps (relances floues, contexte redonné à chaque session…).

## 4. Rapport

Écrire `~/.claude/improve-system/rapports/AAAA-MM-JJ.md`, court :

```
# Amélioration système — <date> (<N> sessions)
## Top 3 (à faire en priorité)
## 1. Ce que Claude rate         → règle exacte à ajouter + fichier cible
## 2. Skills à créer             → nom, déclencheur, étapes, preuve (sessions citées)
## 3. Automatisations            → quoi, comment, temps gagné
## 4. Ménage
## 5. Pour toi
```

Chaque reco = numérotée, 1 preuve (date + projet + citation courte), le texte EXACT à coller. 10 recos max.
Puis `python ~/.claude/skills/improve-system/digest.py --mark`.

## 5. Appliquer

Quand l'utilisateur répond « applique 1, 3, 5 » (ou « tout ») : faire les modifs (CLAUDE.md, mémoire, nouveau skill dans
`~/.claude/skills/<nom>/SKILL.md`), puis cocher les recos dans le rapport.
