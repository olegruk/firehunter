# firehunter

Этот плагин QGIS предназначен для создания мозаики Sentinel-2 для области, заданной прямоугольным выделением.
Мозаика строится по заданному интервалу дат и записывается в отдельный слой с именем, включающим начальную и конечную дату построения мозаики.
Кроме того плагин позволяет создать отдельные слои со снимками Sentinel-2 за даты, попавшие в указанный интервал.

Плагин устанавливается в меню Raster и создает три кнопки на панели инструментов и три пункта в меню "Raster -> Fire Hunter".

В состав плагина входят следующие инструменты:
Make a Sentinel-2 mosaic
Make a Sentinel-2 2-day mosaic
Make a Sentinel-hub link

1. Make a Sentinel-2 mosaic

Для начала работы с инструментом необходимо нажать кнопку (или воспользоваться меню) и курсором выделить на карте прямоугольную область.

В появившемся окне "Get Sentinel-2 images" необходимо задать интервал дат для формирования мозаики. 
Интервал может быть задан двумя способами:
- В поле "Date (last date for mosaic)" указать конечную дату интервала, а в поле "Interval (days before "Date")" указать количество дней в интервале.
- Определить конечную дату интервала, основываясь на датах термоточек, попавших в выделенную область. Для этого нужно отметить пункт "Get dates interval from points layer" и в поле "Points layer" указать слой, из которого будут взяты термоточки. Дата будет определена по дате появления самой последней термоточки. Если в слое будут выделенные точки, то будет доступен для отметки пункт "Selected features only", который позволит определять дату, основываясь только на отмеченных точках. (Внимание! При этом способе дата в поле "Date (last date for mosaic)" меняться не будет!)

Для того, чтобы кроме слоя мозаики были созданы  дополнительные слои за отдельные даты, необходимо отметить пункт "Generate single-date layers".
В имени каждого слоя будет присутствовать дата, за которую он создан.
Для создания композитного слоя необходимо отметить пункт "Generate composite layer".

По умолчанию имя слоя формируется как S2SRC_YYYY-MM-DD, однако можно добавить к имени слоя префикс, указав его в поле "Layer prefix". Все создаваемые слои помещаются в группу "S2SRC"

Плагин также позволяет настраивать комбинацию каналов для отображения. По умолчанию стоит вариант "Произвольная комбинация каналов" (Custom), при которой в полях "Band1 (red)", "Band2 (green)", "Band3 (blue)" могут быть выбраны произвольные каналы. Также можно выбрать стандартные варианты комбинаций: True color', 'False color', 'False color (urban)', 'SWIR'.

Кроме настройки комбинации каналов для формирования мозаики может быть включен или выключен фильтр облачности (пункт "Apply cloud filter") и задан порог облачности, определяющий использование точек снимков для формирования мозаики (поле "Cloudness").
Внимание! Для снимков за отдельные даты фильтр облачности всегда отключен, независимо от установки параметров мозаики.

Параметр "Make result layer visible" определяет будут или нет отображаться созданные слои. По умолчанию слои отображаются.

После нажатия кнопки "Run" плагин выполнит формирование слоев. Признаком завершения работы плагина будет появление на экране сообщения "Loading resulting layers
Algorithm 'Get Sentinel2 images' finished".

Плагин использует в своей работе Google Earth Engine и источник COPERNICUS/S2. 
Для использования плагина также должен быть установлен плагин QGIS Google Earth Engine и зарегистрирована ваша учетная запись в Google Earth Engine.

2. Make a Sentinel-2 2-day mosaic

Инструмент аналогичен инструменту Make a Sentinel-2 mosaic, но диапазон дат по умолчанию установлен в 2 дня.

3. Make a Sentinel-hub link

Для начала работы с инструментом необходимо нажать кнопку (или воспользоваться меню) и курсором отметить на карте точку.
В результате работы будет сформирована ссылка на https://apps.sentinel-hub.com/eo-browser/, которая отобразит снимок в комбинации каналов SWIR с центром в точке, указанной курсором и увеличением (zoom) 13.
