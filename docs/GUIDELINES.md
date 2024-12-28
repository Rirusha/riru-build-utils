# _Rirusha average project_ guidelines

Правила для оформления репозитория RAA (_Rirusha average project_)

1. RAA Должен содержать актуальный шаблон .spec файла. Версия должны быть равна @VERSION@, а блока %changelog быть не должно (Если он есть, то всё равно использоваться не будет).
Если .spec файла нет, то необходимо создать его, выполнив `rbu create` в корневой директории проекта.
2. Если проект содержит в зависимостях другие _Rirusha average project_, то директория subprojects должны иметь wrap файлы с ними, а они в свою очередь должны иметь в revision тег. Не допускается использование коммита или названия ветки.
3. При создании нового проекта, должен быть создан алиас на него в `data/aliases.db`. Файл представляет собой файл со строками `ключ=значение`, где `ключ` - имя проекта, а `значение` - ссылка на .git репозиторий.