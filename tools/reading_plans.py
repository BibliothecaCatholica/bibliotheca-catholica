"""Dated reading plans (v20). Each day points at a passage in a hosted reading-room edition.

Fields per day: d (ISO date), m (liturgical marker or ''), w (work id), e (edition id),
at (paragraph index the link scrolls to, usually the chapter heading), p (first, last) paragraph
indexes of the passage itself, a (author name for the site's author link, when the work collects several authors).
The words readers see (liturgical day, title, theme, excerpt, attribution, reflection, intro) are NOT here: they live in
the plan's `text` file (data/advent-2026.json), the one source of truth that the site page and the Substack posts both
read from. This file only anchors each day to its passage in a hosted edition.
Paragraph indexes are the reader's own: splitText() on the hosted TXT (blank-line blocks), the
same numbers as the `reading-p-<index>` ids. Sections are 35 paragraphs (`size` in read()).

EDITION_YEARS gives each edition used a year before 1931 and the evidence for it. `kind` says what
the year is: 'edition' (title page or edition note) or 'translator' (the translator's death year,
used only when the file names no edition year, as the latest date the translation can have).
tools/build_reading_plans.py validates everything and writes data/reading-plans.json/.js.
"""
EDITION_YEARS={
 'pg-77576':(1870,'edition','Ante-Nicene Christian Library, vol. I, T. & T. Clark, Edinburgh, 1870 (edition note)'),
 'pg-45305':(1871,'edition','T. & T. Clark, Edinburgh, 1871 (title page, MDCCCLXXI)'),
 'pg-3296':(1882,'translator','Translated by E. B. Pusey (1800 to 1882); the file names no edition year'),
 'pg-7403':(1905,'edition','Vida D. Scudder\'s translation, first published 1905 (edition note)'),
 'pg-1653':(1910,'translator','Translated by William Benham (1831 to 1910); the file names no edition year'),
 'pg-38326':(1907,'edition','A. M. Sellar\'s revised translation, George Bell and Sons, London, 1907 (title page)'),
 'pg-72411':(1852,'edition','Second American edition, Edward Dunigan and Brother, New York, 1852 (edition note)'),
 'pg-22295':(1914,'edition','Hugh Pope\'s translation, R. & T. Washbourne, London, 1914 (edition note)'),
 'pg-52958':(1901,'edition','Grace Warrack\'s version, Methuen, London, 1901 (title page)'),
 'pg-14328':(1897,'edition','H. R. James\'s translation, Elliot Stock, London, 1897 (title page)'),
 'pg-52057':(1887,'edition','Ella McMahon\'s translation, Benziger Brothers, New York, 1887 (title page and copyright line)'),
 'pg-48927':(1910,'edition','Longmans, Green and Co. school edition, 1910 printing (edition note)'),
 'pg-1004':(1882,'translator','Translated by Henry Wadsworth Longfellow (1807 to 1882); the file names no edition year'),
 'pg-16772':(1922,'edition','T. N. Taylor\'s edition, Burns, Oates & Washbourne, 1912; 8th ed., 1922 (electronic edition note)'),
}
def D(d,w,e,at,p,a=''):return dict(d=d,w=w,e=e,at=at,p=list(p),a=a)
PLANS=[dict(
 id='advent-2026',text='data/advent-2026.json',
 days=[
 D('2026-11-29','apostolic-fathers','pg-77576',117,(118,118),'Clement of Rome'),
 D('2026-11-30','city-of-god','pg-45305',1312,(1313,1314)),
 D('2026-12-01','confessions','pg-3296',15,(16,17)),
 D('2026-12-02','catherine-letters','pg-7403',625,(625,628)),
 D('2026-12-03','imitation-of-christ','pg-1653',206,(208,209)),
 D('2026-12-04','city-of-god','pg-45305',989,(990,991)),
 D('2026-12-05','bede-ecclesiastical-history','pg-38326',496,(496,496)),
 D('2026-12-06','apostolic-fathers','pg-77576',3885,(3886,3886),'Letter to Diognetus (anonymous)'),
 D('2026-12-07','confessions','pg-3296',150,(150,151)),
 D('2026-12-08','glories-of-mary','pg-72411',617,(618,620)),
 D('2026-12-09','apostolic-fathers','pg-77576',3889,(3890,3890),'Letter to Diognetus (anonymous)'),
 D('2026-12-10','aquinas-prayer-contemplative','pg-22295',494,(495,501)),
 D('2026-12-11','city-of-god','pg-45305',992,(993,993)),
 D('2026-12-12','revelations-divine-love','pg-52958',259,(259,259)),
 D('2026-12-13','city-of-god','pg-45305',1009,(1010,1011)),
 D('2026-12-14','consolation-philosophy','pg-14328',746,(747,748)),
 D('2026-12-15','city-of-god','pg-45305',1012,(1012,1012)),
 D('2026-12-16','abandonment','pg-52057',143,(145,148)),
 D('2026-12-17','dream-gerontius','pg-48927',288,(289,292)),
 D('2026-12-18','city-of-god','pg-45305',1003,(1004,1004)),
 D('2026-12-19','imitation-of-christ','pg-1653',893,(896,898)),
 D('2026-12-20','divine-comedy','pg-1004',4882,(4883,4895)),
 D('2026-12-21','apostolic-fathers','pg-77576',1950,(1952,1952),'Ignatius of Antioch'),
 D('2026-12-22','city-of-god','pg-45305',1041,(1042,1042)),
 D('2026-12-23','city-of-god','pg-45305',1037,(1038,1038)),
 D('2026-12-24','story-of-a-soul','pg-16772',299,(300,302)),
 ])]
