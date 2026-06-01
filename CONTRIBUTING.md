# Contributing Guide

Этот документ описывает простой Git-flow для нашего проекта.\
**Рекомендация, не обязательное требование.**

Главная идея: `main` должен оставаться рабочим. Новые изменения не вливаются в
`main` напрямую, а проходят через отдельную ветку и Pull Request.

---

## 1. Основные правила

- Не отправлять изменения напрямую в `main`.
- Для каждой задачи создавать отдельную ветку.
- Вливать изменения в `main` только через Pull Request.
- Перед Pull Request проверять, что проект запускается и в коммит не попали
  лишние файлы.

---

## 2. Имена веток

Использовать формат:

```text
<type>/<short-description>
```

Основные типы:

```text
feature/add-login
fix/file-upload-error
docs/update-readme
refactor/split-parser
test/add-parser-tests
chore/update-gitignore
```

Правила:

- писать маленькими буквами;
- разделять слова через `-`;
- называть ветку так, чтобы было понятно, какая задача в ней решается.

Плохие примеры:

```text
my-work
final-version
fix
test123
new_branch
```

---

## 3. Сообщения коммитов

Использовать формат:

```text
<type>: <short description>
```

Примеры:

```text
feat: add file category detection
fix: handle empty inbox folder
docs: update setup instructions
refactor: simplify file processor
test: add tests for category matching
chore: update gitignore
```

Разрешенные типы:

| Type | Когда использовать |
|---|---|
| `feat` | новая функциональность |
| `fix` | исправление ошибки |
| `docs` | документация |
| `refactor` | изменение кода без изменения поведения |
| `test` | тесты |
| `chore` | служебные изменения: конфиги, зависимости, `.gitignore` |

Один коммит должен описывать одно логическое изменение.

---

## 4. Типичный flow: от фичи до Pull Request

Допустим, задача: добавить обработку новой категории файлов.

### Шаг 1. Обновить `main`

```bash
git checkout main
git pull origin main
```

### Шаг 2. Создать ветку под задачу

```bash
git checkout -b feature/add-new-file-category
```

### Шаг 3. Сделать изменения в коде

После правок проверить, какие файлы изменились:

```bash
git status
```

### Шаг 4. Добавить файлы в коммит

Если нужно добавить конкретные файлы:

```bash
git add src/file_processor.py tests/test_file_processor.py
```

Если все измененные файлы точно нужны:

```bash
git add .
```

### Шаг 5. Создать коммит

```bash
git commit -m "feat: add new file category"
```

### Шаг 6. Проверить проект

Если в проекте есть тесты:

```bash
python -m pytest
```

Если тестов нет, запустить проект вручную и проверить измененный сценарий.

### Шаг 7. Отправить ветку на GitHub

```bash
git push -u origin feature/add-new-file-category
```

### Шаг 8. Создать Pull Request

Pull Request можно создать через GitHub в браузере:

```text
from: feature/add-new-file-category
to: main
```

Или через терминал, если установлен GitHub CLI:

```bash
gh pr create --base main --head feature/add-new-file-category --title "feat: add new file category" --body "Added processing for a new file category."
```

Если GitHub CLI еще не настроен, один раз выполнить:

```bash
gh auth login
```

В описании PR коротко указать, что изменено и как это проверить:

```md
## Что изменено

Добавлена обработка новой категории файлов.

## Как проверить

1. Положить тестовый файл в папку inbox.
2. Запустить проект.
3. Проверить, что файл попал в правильную категорию.
```

После проверки и обсуждения PR можно вливать в `main`.

---

## 5. Если в Pull Request попросили правки

Оставаться в той же ветке, внести изменения и сделать новый коммит:

```bash
git status
git add .
git commit -m "fix: update category matching"
git push
```

Pull Request обновится автоматически.

---

## 6. Если что-то пошло не так

Сначала посмотреть состояние репозитория:

```bash
git status
git branch
git log --oneline --decorate -5
```

Не использовать без понимания:

```bash
git reset --hard
git rebase
git push --force
git cherry-pick
```

Эти команды могут удалить локальные изменения или переписать историю. Если нет
уверенности, лучше спросить команду.

---

## Короткая версия

```bash
git checkout main
git pull origin main
git checkout -b feature/task-name

# make changes

git status
git add .
git commit -m "feat: short description"
python -m pytest
git push -u origin feature/task-name
gh pr create --base main --head feature/task-name --title "feat: short description" --body "Short PR description."
```

После этого Pull Request можно проверить и отправить на ревью.
