"""Dated reading plans (v20). Each day points at a passage in a hosted reading-room edition.

Fields per day: d (ISO date), m (liturgical marker or ''), w (work id), e (edition id),
at (paragraph index the link scrolls to, usually the chapter heading), p (first, last) paragraph
indexes of the passage itself, ref (where it is in the work), note (short, factual), a (author shown, when the work collects several authors).
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
def D(d,m,w,e,at,p,ref,note,a=''):return dict(d=d,m=m,w=w,e=e,at=at,p=list(p),ref=ref,note=note,a=a)
PLANS=[dict(
 id='advent-2026',t='Advent with the Fathers',year=2026,start='2026-11-29',end='2026-12-24',
 sub='Twenty-six short readings for Advent 2026, from the Fathers and the classic Catholic writers in our reading room',
 intro='Advent 2026 begins on Sunday, November 29, and ends on Christmas Eve. This plan gives one short reading for each of its 26 days, drawn only from the public-domain editions in our reading room. The first weeks look toward Christ’s coming at the end of time; from December 17 the readings follow the O Antiphons toward Christmas. Each link opens the reader at the start of the passage.',
 days=[
 D('2026-11-29','First Sunday of Advent','apostolic-fathers','pg-77576',117,(118,118),'First Epistle of Clement, chapter XXIII','Clement of Rome wrote to the church at Corinth near the end of the first century. This chapter answers those who doubt that what was promised will come to pass.','Clement of Rome'),
 D('2026-11-30','St Andrew, Apostle','city-of-god','pg-45305',1312,(1313,1314),'Book XX, chapter 1','Book XX of The City of God is on the Last Judgment. Augustine begins with what the whole Church professes: that Christ shall come from heaven to judge the living and the dead.'),
 D('2026-12-01','','confessions','pg-3296',15,(16,17),'Book I, opening','The opening of the Confessions, written about 397 to 400. Augustine asks how the God who made heaven and earth can come into him.'),
 D('2026-12-02','','catherine-letters','pg-7403',625,(625,628),'Letter to Stefano Maconi','Catherine of Siena (1347 to 1380) writes on keeping watch over the soul. Her closing lines mention her arrival in Rome on the first Sunday in Advent.'),
 D('2026-12-03','St Francis Xavier','imitation-of-christ','pg-1653',206,(208,209),'Book II, chapter 1, “Of the inward life”','The Imitation of Christ, usually attributed to Thomas à Kempis (about 1380 to 1471), on preparing the heart for Christ to come and dwell within.'),
 D('2026-12-04','','city-of-god','pg-45305',989,(990,991),'Book XVIII, chapter 29','In Book XVIII Augustine surveys the prophets. This chapter gathers what Isaiah foretold of Christ and the Church.'),
 D('2026-12-05','','bede-ecclesiastical-history','pg-38326',496,(496,496),'Book IV, chapter 3','Bede (about 673 to 735) on the death of St Chad (Ceadda), bishop of the Mercians, who kept the day of the Lord always in mind.'),
 D('2026-12-06','Second Sunday of Advent','apostolic-fathers','pg-77576',3885,(3886,3886),'Epistle to Diognetus, chapter VII','An anonymous early Christian letter of uncertain date, printed in this edition with the Apostolic Fathers. Chapter VII is on how God sent His Word among men.','Letter to Diognetus (anonymous)'),
 D('2026-12-07','St Ambrose','confessions','pg-3296',150,(150,151),'Book V','Augustine describes coming to Milan in 384 and hearing Bishop Ambrose preach.'),
 D('2026-12-08','Immaculate Conception of the Blessed Virgin Mary','glories-of-mary','pg-72411',617,(618,620),'Discourse on the Immaculate Conception','Alphonsus Liguori (1696 to 1787) published The Glories of Mary in 1750. Pius IX defined the Immaculate Conception as dogma in 1854, after this discourse was written.'),
 D('2026-12-09','','apostolic-fathers','pg-77576',3889,(3890,3890),'Epistle to Diognetus, chapter IX','Chapter IX, “Why the Son was sent so late,” takes up the question of why God waited so long.','Letter to Diognetus (anonymous)'),
 D('2026-12-10','','aquinas-prayer-contemplative','pg-22295',494,(495,501),'On the seven petitions of the Lord’s Prayer','From the Summa Theologiae (II-II, question 83, article 9) in Hugh Pope’s 1914 translation. Aquinas explains what we ask when we pray “Thy kingdom come.”'),
 D('2026-12-11','','city-of-god','pg-45305',992,(993,993),'Book XVIII, chapter 30','Augustine reads Micah, including the prophecy that a ruler of Israel will come out of Bethlehem.'),
 D('2026-12-12','Our Lady of Guadalupe','revelations-divine-love','pg-52958',259,(259,259),'Chapter IV','Julian of Norwich (about 1342 to after 1416) recorded the showings she received in May 1373. Here she sees Mary as she was when she conceived.'),
 D('2026-12-13','Third Sunday of Advent (Gaudete Sunday)','city-of-god','pg-45305',1009,(1010,1011),'Book XVIII, chapter 35','Haggai and Zechariah. Augustine quotes Zechariah: “Rejoice greatly, O daughter of Sion.” Gaudete Sunday is named for the first word of its entrance antiphon, Rejoice.'),
 D('2026-12-14','St John of the Cross','consolation-philosophy','pg-14328',746,(747,748),'Book V, prose VI','Boethius (about 477 to 524) wrote The Consolation of Philosophy in prison. Here Philosophy explains that God lives in an eternal present.'),
 D('2026-12-15','','city-of-god','pg-45305',1012,(1012,1012),'Book XVIII, chapter 35 (continued)','The same chapter turns to Malachi, including the promise of the messenger sent to prepare the way.'),
 D('2026-12-16','','abandonment','pg-52057',143,(145,148),'Book I, chapter II','Jean-Pierre de Caussade (1675 to 1751) on finding God’s will in the duties of each moment, beginning from the angel’s words to Mary.'),
 D('2026-12-17','O Sapientia (O Wisdom)','dream-gerontius','pg-48927',288,(289,292),'The Fifth Choir of Angelicals','The O Antiphons are sung at Vespers from December 17 to 23. Newman’s hymn, “Praise to the Holiest in the height,” praises the “loving wisdom of our God.”'),
 D('2026-12-18','O Adonai (O Lord)','city-of-god','pg-45305',1003,(1004,1004),'Book XVIII, chapter 33','Jeremiah’s prophecies as Augustine reads them, including the righteous shoot to be raised up for David.'),
 D('2026-12-19','O Radix Jesse (O Root of Jesse)','imitation-of-christ','pg-1653',893,(896,898),'Book IV, chapter 17','“Of fervent love and vehement desire of receiving Christ.” The chapter recalls John the Baptist, who leapt for joy in his mother’s womb.'),
 D('2026-12-20','Fourth Sunday of Advent; O Clavis David (O Key of David)','divine-comedy','pg-1004',4882,(4883,4895),'Paradiso, Canto XXXIII','The last canto of the Divine Comedy opens with St Bernard of Clairvaux’s prayer to the Virgin, in Longfellow’s translation.'),
 D('2026-12-21','O Oriens (O Dayspring)','apostolic-fathers','pg-77576',1950,(1952,1952),'Ignatius, Epistle to the Ephesians, chapter XIX (shorter version)','Ignatius of Antioch wrote this letter on his way to martyrdom in Rome early in the second century. Chapter XIX tells of the star.','Ignatius of Antioch'),
 D('2026-12-22','O Rex Gentium (O King of the Nations)','city-of-god','pg-45305',1041,(1042,1042),'Book XVIII, chapter 48','Augustine on Haggai’s prophecy that the glory of the latter house will be greater than the first, when “the desired of all nations” comes.'),
 D('2026-12-23','O Emmanuel','city-of-god','pg-45305',1037,(1038,1038),'Book XVIII, chapter 46','Augustine on the birth of Christ in Bethlehem while Herod reigned in Judea, citing the prophecy of the virgin who will bear a Son called Immanuel.'),
 D('2026-12-24','Christmas Eve','story-of-a-soul','pg-16772',299,(300,302),'Chapter V, “Vocation of Thérèse”','Thérèse of Lisieux (1873 to 1897) describes the grace she received at Christmas 1886, after Midnight Mass.'),
 ])]
