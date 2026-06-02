# Настройка бота в BotFather

## Описание бота (Description)

Скопируйте текст из файла `bot_description.txt` и отправьте в BotFather:

1. Откройте @BotFather
2. Отправьте `/mybots`
3. Выберите вашего бота
4. Нажмите "Edit Bot" → "Edit Description"
5. Вставьте текст из `bot_description.txt`

---

## Короткое описание (About)

Для короткого описания используйте:

```
Подбираю фильмы под твоё настроение. Просто расскажи, что хочется посмотреть! 🎬
```

Как установить:
1. @BotFather → `/mybots`
2. Выберите бота → "Edit Bot" → "Edit About"
3. Вставьте текст выше

---

## Баннер (Bot Picture)

Конвертируйте `bot_banner.svg` в PNG (1280x640px):

### Онлайн способ:
1. Откройте https://cloudconvert.com/svg-to-png
2. Загрузите `bot_banner.svg`
3. Установите размер 1280x640
4. Скачайте PNG

### Через командную строку (если установлен ImageMagick):
```bash
magick convert -density 300 -background none bot_banner.svg -resize 1280x640 bot_banner.png
```

Затем:
1. @BotFather → `/mybots`
2. Выберите бота → "Edit Bot" → "Edit Botpic"
3. Загрузите `bot_banner.png`

---

## Аватар бота (Profile Picture)

Используйте текущий логотип `logo.svg` и конвертируйте в PNG (512x512px):

### Онлайн способ:
1. Откройте https://cloudconvert.com/svg-to-png
2. Загрузите `miniapp/static/logo.svg`
3. Установите размер 512x512
4. Скачайте PNG

### Через командную строку:
```bash
magick convert -density 300 -background none miniapp/static/logo.svg -resize 512x512 bot_avatar.png
```

Затем:
1. @BotFather → `/setuserpic`
2. Выберите бота
3. Загрузите `bot_avatar.png`

---

## Команды бота (Commands)

Установите команды:

1. @BotFather → `/mybots`
2. Выберите бота → "Edit Bot" → "Edit Commands"
3. Отправьте:

```
start - Начать поиск фильма
```

---

## Настройка Mini App

### 1. Создание Mini App в BotFather

1. Откройте @BotFather
2. Отправьте `/newapp`
3. Выберите вашего бота
4. **URL**: `https://imply-santa-confident.ngrok-free.dev/`
5. **Launch mode**: выберите `fullscreen` (для полноэкранного режима)
6. **Splash icon** (512x512px): Конвертируйте `miniapp/static/logo.svg` в PNG

### 2. Конвертация Splash Icon

**Онлайн способ:**
1. Откройте https://cloudconvert.com/svg-to-png
2. Загрузите `miniapp/static/logo.svg`
3. Установите размер **512x512**
4. Скачайте PNG и загрузите в BotFather

**Через командную строку:**
```bash
magick convert -density 300 -background none miniapp/static/logo.svg -resize 512x512 splash_icon.png
```

### 3. Настройка Menu Button

Добавьте кнопку Mini App в меню чата:

1. @BotFather → `/mybots`
2. Выберите бота → "Bot Settings" → "Menu Button"
3. **Configure menu button**:
   - **URL**: `https://imply-santa-confident.ngrok-free.dev/`
   - **Title**: `Открыть Кинотавр` или `🎬 Подобрать фильм`

Теперь пользователи увидят кнопку Mini App в меню (≡) рядом с полем ввода!

### 4. Обновление URL при смене хостинга

Если вы переедете с ngrok на постоянный хостинг:

1. **Для Mini App**: @BotFather → `/myapps` → выберите ваше приложение → измените URL
2. **Для Menu Button**: @BotFather → `/mybots` → Bot Settings → Menu Button → измените URL
3. Обновите `WEBAPP_URL` в `.env`
4. Перезапустите бота

---

## Чек-лист настройки

- [ ] Описание бота (Description)
- [ ] Короткое описание (About)
- [ ] Баннер (Botpic) - 1280x640px
- [ ] Аватар (Profile Picture) - 512x512px
- [ ] Команды (/start)
- [ ] **Mini App создан (/newapp) с URL и Splash Icon**
- [ ] **Launch mode установлен на fullscreen**
- [ ] **Menu Button настроена с URL и Title**
- [ ] Кнопка Mini App в сообщении /start (уже настроена в коде)

После всех настроек ваш бот будет выглядеть профессионально! 🎬
