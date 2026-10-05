# Improve System — ton IA qui s'améliore toute seule

Un skill pour **Claude Code** qui relit tes conversations avec Claude et te sort un rapport :

- les erreurs que Claude refait ;
- les questions que tu lui reposes chaque semaine (→ un skill à créer) ;
- les tâches répétitives à automatiser ;
- les skills installés que tu n'utilises jamais.

Tu valides les recos (« applique 1, 3, 5 » ou « applique tout ») et il met à jour ses propres règles.

**100 % local** : il lit les fichiers de conversation que Claude Code garde déjà sur ton ordi (`~/.claude/projects/`).
Rien n'est envoyé ailleurs. Le rapport est écrit dans `~/.claude/improve-system/rapports/`.

## Installation

Il te faut **Claude Code** et **Python 3**.

**Le plus simple** : colle ça dans Claude Code.

```
Installe le skill improve-system depuis https://github.com/armandhespel-coder/improve-system :
copie le dossier improve-system/ du repo dans ~/.claude/skills/, puis lance
python ~/.claude/skills/improve-system/digest.py --days 7 et dis-moi combien de sessions il a trouvées.
```

**À la main** :

```
git clone https://github.com/armandhespel-coder/improve-system
cp -r improve-system/improve-system ~/.claude/skills/
```

## Utilisation

Dans Claude Code, tape `/improve-system` (une à deux fois par semaine, c'est l'idéal).
Lis le rapport, puis réponds « applique 1, 3 » pour appliquer les recos qui te plaisent.

Pour une période précise : « /improve-system sur les 30 derniers jours ».

## Ce qu'il y a dedans

- `improve-system/SKILL.md` — les instructions pour Claude (analyse, format du rapport, application).
- `improve-system/digest.py` — résume tes sessions récentes en un fichier compact (messages, commandes, erreurs
  d'outils, corrections), pour que Claude n'ait pas à lire des mégaoctets de logs.

## Licence

MIT — fais-en ce que tu veux.

---

Fait par Armand · [Aptibots](https://aptibots.com)
