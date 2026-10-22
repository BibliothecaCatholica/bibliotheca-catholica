# Curated reading lists. e = editions-guide id (buy links + free texts come from there).
# Items without e carry their own isbn (verified on Open Library) or none (search link).
G='https://www.gutenberg.org/ebooks/'; SE='https://standardebooks.org/ebooks/'; NA='https://www.newadvent.org/'
def I(e=None,b='',t='',a='',isbn='',free=None,pk=''): return dict(e=e,b=b,t=t,a=a,isbn=isbn,free=free or [],pk=pk)
L=[
dict(id='start',t='Start Here',sub='New to Catholicism, coming home, or just curious',ic='✠',items=[
 I('bible','Begin with the Gospels in a good Catholic translation; Mark is shortest, John is deepest.'),
 I('ccc','Use the Compendium for a first pass, the full Catechism as your reference.'),
 I('catholicism','The best single tour of the faith through its beauty, saints, and story.'),
 I('kreeft','Every major doctrine explained in plain, lively prose.'),
 I('theologysanity','Why believing these things makes you saner, not narrower.'),
 I('orthodoxy','Chesterton discovers he has re-invented Christianity, only to find it was already there.'),
 I('confessions','The restless heart that found its rest: still the great conversion story.'),
 I('romesweethome','A Presbyterian minister and his wife follow Scripture into the Church.'),
 I('storysoul','Holiness is for everyone: the Little Way.'),
 I('devout','How to live a devout life in the world, with a job and a family.'),
 I('jesus_naz','Benedict XVI introduces you to the Person at the centre of it all.'),
 I('imitation','Short chapters for daily reading, read by saints for 600 years.')]),
dict(id='apologetics',t='Apologetics',sub='Reasons for the hope that is in you (1 Pet 3:15)',ic='⚔',items=[
 I('handbook','Arguments for God, Christ, and the Church, compactly organised.'),
 I('keating','The classic answer to fundamentalist objections.'),
 I('fathersknow','What the early Church actually believed, topic by topic.'),
 I('apfathers','Read the sources yourself: bishops who knew the Apostles.'),
 I('everlasting','History’s long view: man is not just an animal, and Christ is not just a man.'),
 I('orthodoxy','The imaginative case for Christianity.'),
 I('development','Newman’s answer to “Isn’t Catholic doctrine a corruption?”'),
 I('pensees','The wager, the heart’s reasons, and the misery and greatness of man.'),
 I(None,'Knox’s lucid 1927 case for the Church, back in print.','The Belief of Catholics','Ronald Knox','9781685950729',pk='cluny'),
 I('intro_xty','Ratzinger on what it means to say “I believe.”')]),
dict(id='spiritual',t='Spiritual Classics',sub='The books the saints read',ic='❦',items=[
 I('imitation','The handbook of interior life.'),
 I('devout','Prayer, virtue, and friendship for lay people.'),
 I('storysoul','Confidence and love: the Little Way.'),
 I('teresa','The seven mansions of the soul.'),
 I('johncross','Purification, darkness, and union.'),
 I('exercises','The Ignatian method of prayer and discernment.'),
 I('spiritualcombat','Practical warfare against the self.'),
 I('caussade','God’s will in the present moment.'),
 I('presence','Prayer among the pots and pans.'),
 I('cloud','Contemplation beyond concepts.'),
 I('julian','“All shall be well, and all manner of thing shall be well.”'),
 I('faustina','Jesus, I trust in You.')]),
dict(id='fiction',t='Fiction & Literature',sub='Grace in story and verse',ic='✒',items=[
 I('dante','The supreme Catholic poem; read Esolen’s notes as you go.'),
 I('brideshead','Grace pursues a family “by a twitch upon the thread.”'),
 I('lotr','A fundamentally religious and Catholic work, unconsciously at first and then consciously.'),
 I('oconnor','Grace arriving violently in the American South.'),
 I('kristin','Medieval Norway, a woman’s sin, and the long road to sanctity.'),
 I('bernanos','A young priest’s hidden holiness: “Grace is everywhere.”'),
 I('betrothed','Providence and conversion in plague-time Lombardy.'),
 I('greene','The whisky priest, the last priest in his state, still bringing the sacraments.'),
 I('percy','A New Orleans stockbroker on “the search.”'),
 I('lordworld','The Antichrist arrives as a humanitarian; written in 1907.'),
 I('cather','Missionary bishops in the New Mexico desert.'),
 I('hopkins','The world is charged with the grandeur of God.')]),
dict(id='waugh',t='Waugh Starter',sub='For a reading group beginning Evelyn Waugh, in a suggested order',ic='W',items=[
 I(None,'Start with the comedy: savage, hilarious, and public domain in the U.S. since 2024.','Decline and Fall (1928)','Evelyn Waugh','9780316926072',[['Standard Ebooks',SE+'evelyn-waugh/decline-and-fall']],'littlebrown'),
 I(None,'Bright Young Things and the void beneath them; public domain since 2026.','Vile Bodies (1930)','Evelyn Waugh','9780316926119',[['Standard Ebooks',SE+'evelyn-waugh/vile-bodies'],['Gutenberg',G+'77900']],'littlebrown'),
 I(None,'The darkest of the satires; the first Waugh after his 1930 conversion.','A Handful of Dust (1934)','Evelyn Waugh','9780316926058',pk='littlebrown'),
 I(None,'His newspaper satire, the funniest book he wrote.','Scoop (1938)','Evelyn Waugh','9780316926102',pk='littlebrown'),
 I('brideshead','The great Catholic novel. Read it after the comedies to feel the change.'),
 I(None,'Waugh’s favourite of his novels: St. Helena and the finding of the True Cross.','Helena (1950)','Evelyn Waugh',''),
 I(None,'The war trilogy: Guy Crouchback’s Catholic vocation amid the collapse of honour.','Sword of Honour (1952–61)','Evelyn Waugh','9780316216692',pk='littlebrown'),
 I(None,'Waugh’s life of the Jesuit martyr; written as thanks for his reception.','Edmund Campion (1935)','Evelyn Waugh','9781586170431',pk='ignatius')]),
dict(id='chesterton',t='The Chesterton Shelf',sub='Start anywhere; he is never dull. Read alongside our featured Chesterton column.',ic='GKC',items=[
 I('orthodoxy','Start here: his own road to faith.'),
 I('everlasting','The answer to H. G. Wells, and the book that helped convert C. S. Lewis.'),
 I('fatherbrown','The priest-detective; start with The Innocence of Father Brown.'),
 I('thursday','A nightmare-comedy that turns into a vision.'),
 I(None,'Twenty essays on the great men of his day, and why they were wrong.','Heretics (1905)','G. K. Chesterton','',[['Standard Ebooks',SE+'g-k-chesterton/heretics'],['Gutenberg',G+'470']]),
 I('ckaquinas','Gilson said the Aquinas was the best book ever written on Thomas.'),
 I(None,'A London borough goes to war for its lamp-posts.','The Napoleon of Notting Hill (1904)','G. K. Chesterton','',[['Standard Ebooks',SE+'g-k-chesterton/the-napoleon-of-notting-hill'],['Gutenberg',G+'20058']]),
 I(None,'Family, property, and the case for distributism.','What’s Wrong with the World (1910)','G. K. Chesterton','',[['Standard Ebooks',SE+'g-k-chesterton/whats-wrong-with-the-world']]),
 I(None,'An atheist and a Catholic try to fight a duel and keep getting interrupted.','The Ball and the Cross (1909)','G. K. Chesterton','',[['Gutenberg',G+'5265']]),
 I(None,'A comic novel about a man who rediscovers life by recapturing his own wife and house.','Manalive (1912)','G. K. Chesterton','',[['Standard Ebooks',SE+'g-k-chesterton/manalive']])]),
dict(id='philosophy',t='Philosophy & Theology',sub='Faith seeking understanding',ic='Φ',items=[
 I('summa','Begin with Kreeft’s Summa of the Summa, then the real thing.'),
 I('feser','Act and potency, the four causes, and the Five Ways, made clear.'),
 I('leisure','Why culture begins in contemplation and worship.'),
 I('gilson','What “Christian philosophy” means, by its great historian.'),
 I('intro_xty','The Creed, article by article.'),
 I('theologysanity','Dogma as the furniture of a sane mind.'),
 I('grammar','How we really come to certainty.'),
 I('idea','The unity of knowledge and the place of theology.'),
 I('cityofgod','Two loves built two cities.'),
 I('pensees','The heart has its reasons.'),
 I('development','How doctrine grows without changing.')]),
dict(id='history',t='Church History',sub='Two thousand years, briefly',ic='†',items=[
 I(None,'The first history of the Church, from the Apostles to Constantine.','Ecclesiastical History','Eusebius of Caesarea','',[['New Advent',NA+'fathers/2501.htm']]),
 I('carroll','Narrative history from a Catholic perspective, beginning with the Founding.'),
 I('dawson','How the Church made Europe.'),
 I('duffy','The vivid world of late-medieval English Catholicism and its destruction.'),
 I(None,'The best one-volume history of the papacy.','Saints and Sinners: A History of the Popes','Eamon Duffy','9780300206128',pk='yale'),
 I('belloc','Belloc’s walk to Rome, and his thesis that “Europe is the Faith.”'),
 I('apologia','The Oxford Movement from the inside.'),
 I('waugh','Edmund Campion: the Elizabethan persecution told by a novelist.')]),
dict(id='saints',t='Saints’ Lives',sub='Friends in high places',ic='☼',items=[
 I('confessions','The first and greatest spiritual autobiography.'),
 I('storysoul','The saint of the Little Way, in her own words.'),
 I('littleflowers','Francis and his first brothers.'),
 I('ckaquinas','Chesterton’s portraits of Thomas and Francis.'),
 I('campion_ck','A saint for every day of the year.'),
 I('faustina','The apostle of Divine Mercy.'),
 I('merton','A modern conversion, all the way to the Trappists.'),
 I('day','From radical journalist to founder of the Catholic Worker.'),
 I(None,'Teresa of Ávila’s own story of her life and prayer.','The Life of St. Teresa of Jesus','St. Teresa of Ávila','',[['Gutenberg',G+'8120']]),
 I('apologia','The autobiography of a saint and Doctor of the Church.')]),
dict(id='liturgy',t='Liturgy',sub='Lex orandi, lex credendi',ic='☧',items=[
 I('spirit_lit','Why we face East, why sacred music, why beauty matters.'),
 I('lambssupper','The Mass as heaven on earth, read through Revelation.'),
 I('pitre','The Last Supper in its Jewish context.'),
 I(None,'The 1918 classic that started the liturgical movement: liturgy as holy play.','The Spirit of the Liturgy','Romano Guardini',''),
 I(None,'The great 15-volume commentary on the Church’s year; beautiful for daily reading.','The Liturgical Year','Dom Prosper Guéranger',''),
 I('rule','“Let nothing be preferred to the Work of God.”'),
 I('duffy','What liturgy meant to ordinary medieval Catholics.'),
 I(None,'The prayers and ceremonies of the Mass explained by the great abbot of Solesmes.','The Holy Mass','Dom Prosper Guéranger','9781905574049',pk='baronius')])]

# Guidance describes a suggested first step, not a compulsory sequence.
GUIDANCE = {
 'start': ('New readers', 'Begin with one Gospel, then use the Compendium to look up questions as they arise. Choose one other book that interests you; you do not need to read this whole shelf in order.'),
 'apologetics': ('Questions about the faith', 'Start with one question you actually have. Read an introductory explanation, then follow its references to Scripture and the early Church.'),
 'spiritual': ('Prayer and daily life', 'Begin with Introduction to the Devout Life or a short chapter of The Imitation of Christ. Read slowly and return to a passage in prayer. Retreat exercises are best approached with appropriate guidance.'),
 'fiction': ('Novels and poetry', 'Choose a story you enjoy. The order is a shelf arrangement, not a reading schedule; Dante benefits from an edition with explanatory notes.'),
 'waugh': ('A suggested author sequence', 'Begin with Decline and Fall for the early comedy, or Brideshead Revisited for a more explicitly Catholic novel. Follow the suggested order if you want to trace Waugh’s development.'),
 'chesterton': ('An author to explore', 'Try a Father Brown story first, then Orthodoxy. Move to The Everlasting Man when you want a longer argument about history and Christianity.'),
 'philosophy': ('Sustained study', 'Begin with an introduction such as Theology and Sanity or Aquinas: A Beginner’s Guide. Approach the Summa by question and article, alongside a guide.'),
 'history': ('Historical context', 'Choose an introductory narrative before a specialist study. Compare an author’s interpretation with the primary sources and the period being discussed.'),
 'saints': ('Biography and conversion', 'Start with Story of a Soul or Confessions. Distinguish a saint’s autobiography from later biographies and collections of devotional stories.'),
 'liturgy': ('Understanding worship', 'Begin with one explanation of the Mass. Ratzinger and Guardini wrote different books called The Spirit of the Liturgy; check the author when choosing.'),
}
for shelf in L:
    shelf['audience'], shelf['start'] = GUIDANCE[shelf['id']]
    for item in shelf['items']:
        if item.get('t') == 'The Life of St. Teresa of Jesus':
            item['workIds'] = ['life-of-teresa']
        if shelf['id'] == 'history' and item.get('e') == 'waugh':
            item.update(e=None, t='Edmund Campion', a='Evelyn Waugh', isbn='9781586170431', pk='ignatius')
        if shelf['id'] == 'saints' and item.get('e') == 'apologia':
            item['b'] = 'Newman’s account of his religious development and conversion.'
        if shelf['id'] == 'start' and item.get('e') == 'bible':
            item['b'] = 'Begin with one Gospel in a Catholic translation. Mark offers a compact starting point; read John alongside it when you want to explore further.'

L.extend([
 dict(id='fathers', t='Read the Church Fathers', sub='Short primary texts before the larger collections', ic='☩', audience='First encounters with the Fathers',
      start='Begin with Ignatius’s Letter to the Ephesians, then Athanasius’s On the Incarnation. Read the introductions and translation notes at the original source.',
      items=[dict(workIds=[w], b=b) for w,b in [
       ('ignatius-of-antioch-epistle-to-the-ephesians','A short letter on unity, worship, and life in the early Church.'),
       ('ignatius-of-antioch-epistle-to-the-romans','Ignatius writes about his approaching martyrdom.'),
       ('justin-martyr-first-apology','An early explanation of Christian belief and worship addressed to imperial authorities.'),
       ('athanasius-of-alexandria-on-the-incarnation-of-the-word','A sustained account of the Incarnation and salvation.'),
       ('basil-the-great-de-spiritu-sancto','A more demanding study of the Holy Spirit, worship, and the Trinity.')]]),
 dict(id='documents', t='Read Church Documents', sub='Council constitutions and papal teaching at their official sources', ic='✠', audience='Readers seeking primary sources',
      start='Begin with Dei Verbum for Scripture and Tradition, then Lumen Gentium for the Church. These are selected entry points, not a substitute for reading the documents in context.',
      items=[dict(workIds=[w], b=b) for w,b in [
       ('dei-verbum','Vatican II on revelation, Scripture, and Tradition.'),
       ('lumen-gentium','Vatican II on the Church, holiness, and the people of God.'),
       ('sacrosanctum-concilium','The council’s constitution on the sacred liturgy.'),
       ('deus-caritas-est','Benedict XVI on Christian love and charitable service.'),
       ('fides-ratio','John Paul II on the relationship of faith and reason.'),
       ('rerum-novarum','Leo XIII on workers, property, and the social question.')]]),
 dict(id='related-christian', t='Related Christian Voices', sub='C. S. Lewis in conversation with Catholic readers', ic='✒', audience='Christian apologetics and literature',
      start='Lewis was Anglican. Begin with Mere Christianity for apologetics or The Screwtape Letters for imaginative moral reflection. Open the labeled excerpt or limited preview for each title, then check a library for a complete copy.',
      items=[dict(workIds=[w], b=b) for w,b in [
       ('lewis-mere-christianity','An account of shared Christian belief; read alongside Catholic sources when questions of doctrine arise.'),
       ('lewis-screwtape-letters','A fictional treatment of temptation and the habits of the spiritual life.'),
       ('lewis-abolition-man','A short argument about education, value, and human nature.')]])
])
