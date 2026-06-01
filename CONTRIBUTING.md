# Contributing Guide

## Основной принцип

Ветка `main` должна оставаться рабочей. Поэтому новые изменения сначала делаются в отдельной ветке, затем отправляются через Pull Request.

## Ветки

Для задач использовать такие типы веток:

```text
feature/...
fix/...
test/...
docs/...
```

## Коммиты

Сообщения коммитов писать в формате:

```text
type: short description
```

Примеры:

```text
feat: add processor
fix: handle decode errors
test: add processor tests
docs: update README
```

## Типичный порядок работы

```bash
git checkout main
git pull origin main
git checkout -b feature/task-name

# сделать изменения

git status
git add .
git commit -m "feat: short description"
python -m pytest
git push -u origin feature/task-name
```

## Создание Pull Request

После `git push` Pull Request можно открыть двумя способами.

Через GitHub в браузере:

```text
Repository -> Pull requests -> New pull request
base: main
compare: feature/task-name
Create pull request
```

Или через GitHub CLI:

```bash
gh pr create --base main --head feature/task-name --title "feat: short description" --body "Описание изменений и способ проверки"
```

## Перед Pull Request

Перед отправкой изменений нужно проверить:

```bash
python -m pytest
python src/main.py
```

## Если нужно исправить Pull Request

Если после проверки нашли ошибку, изменения вносятся в той же ветке:

```bash
git status
git add .
git commit -m "fix: short description"
git push
```
