# Размещение презентации на GitHub Pages

GitHub Pages позволяет бесплатно хостить статические сайты прямо из вашего репозитория.

## Способ 1: Через веб-интерфейс GitHub (самый простой)

### Шаг 1: Откройте настройки репозитория
1. Перейдите на https://github.com/vizintini07/tgBot
2. Нажмите на вкладку **Settings** (Настройки)

### Шаг 2: Включите GitHub Pages
1. В левом меню найдите раздел **Pages**
2. В секции **Source** (Источник):
   - Выберите ветку: **main**
   - Выберите папку: **/ (root)**
3. Нажмите **Save**

### Шаг 3: Дождитесь публикации
- GitHub начнёт публикацию (обычно 1-2 минуты)
- После завершения появится зелёный баннер с URL: `https://vizintini07.github.io/tgBot/`

### Шаг 4: Откройте презентацию
Ваша презентация будет доступна по адресу:
```
https://vizintini07.github.io/tgBot/presentation.html
```

---

## Способ 2: Через командную строку (альтернатива)

Если хотите сделать `presentation.html` главной страницей:

### Шаг 1: Переименуйте файл
```bash
git mv presentation.html index.html
git commit -m "Rename presentation to index for GitHub Pages"
git push
```

### Шаг 2: Включите GitHub Pages (как в Способе 1)

Теперь презентация будет доступна просто по адресу:
```
https://vizintini07.github.io/tgBot/
```

---

## Способ 3: Создать отдельную ветку gh-pages (продвинутый)

Если не хотите публиковать весь репозиторий:

```bash
# Создайте ветку gh-pages
git checkout --orphan gh-pages

# Удалите все файлы кроме презентации
git rm -rf .
git checkout main -- presentation.html

# Переименуйте в index.html
mv presentation.html index.html

# Закоммитьте и запушьте
git add index.html
git commit -m "Add presentation to GitHub Pages"
git push origin gh-pages

# Вернитесь в main
git checkout main
```

Затем в Settings → Pages выберите ветку **gh-pages**.

---

## Проверка публикации

1. Откройте **Settings → Pages**
2. Найдите сообщение: "Your site is live at https://vizintini07.github.io/tgBot/"
3. Нажмите на ссылку **Visit site**

---

## Если что-то не работает

### Проблема: Страница не отображается
- Подождите 2-3 минуты после первой публикации
- Проверьте, что файл `presentation.html` действительно есть в main ветке
- Очистите кэш браузера (Ctrl+F5)

### Проблема: Стили не загружаются
- Проверьте пути к изображениям в presentation.html
- Все пути должны быть относительными, не абсолютными

### Проблема: Логотипы не отображаются
Путь `miniapp/static/logo.svg` должен работать автоматически, но если нет:
1. Убедитесь, что папка `miniapp` тоже в репозитории
2. Или скопируйте логотипы в корень рядом с presentation.html

---

## Бонус: Красивый URL

После публикации вы можете:
1. Купить домен (например, kinotavr.ru)
2. В Settings → Pages → Custom domain указать ваш домен
3. Настроить DNS записи у регистратора домена

Или использовать бесплатный поддомен от GitHub: `vizintini07.github.io/tgBot`

---

## Рекомендация

Используйте **Способ 1** - это самый простой и быстрый метод. Просто включите GitHub Pages в настройках репозитория, и всё заработает!

После публикации поделитесь ссылкой:
```
https://vizintini07.github.io/tgBot/presentation.html
```
