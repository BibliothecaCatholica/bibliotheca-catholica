/* Bibliotheca Catholica: affiliate configuration.
 * Paste your IDs below. While a field is empty, every link still works as a plain, non-affiliate link.
 *
 *  bookshopId  Bookshop.org Affiliate ID (sign up: https://bookshop.org/affiliates). Book links become
 *              https://bookshop.org/a/{bookshopId}/{isbn13}, which pays 10% on sales.
 *  publishers[key].wrap
 *              Optional deep-link template from the publisher's affiliate network. Use {url} for the
 *              encoded destination URL, e.g. a CJ link for Ignatius:
 *              'https://www.anrdoezrs.net/click-PID-AID?url={url}'
 *  publishers[key].param
 *              Optional query parameter appended to publisher links instead, e.g. 'ref=bibliotheca'
 *              (Shopify / LeadDyno style programs such as Word on Fire, Sophia, or TAN).
 */
window.AFFILIATES = {
  bookshopId: '130222',
  bookshopShop: '', // blank until the owner creates or confirms the real Bookshop.org shop URL (old /shop/bibliotheca-catholica returned 404, 2026-10-25)
  disclosure: 'Affiliate disclosure: Bookshop.org “Buy” links are affiliate links. If you buy through them, Bibliotheca Catholica earns a small commission at no extra cost to you, which helps keep the library free. Publisher links may become affiliate links too. Commissions never decide what we recommend: editions are chosen on their merits.',
  publishers: {
    ignatius:   { name: 'Ignatius Press',      search: 'https://ignatius.com/search.php?search_query={q}', wrap: '', param: '', program: 'CJ (10%): https://www.ignatius.com/affiliate-programs/' },
    tan:        { name: 'TAN Books',           search: 'https://tanbooks.com/search?q={q}',                wrap: '', param: '', program: 'LeadDyno (8%): https://tanbooks.com/affiliate-program/' },
    sophia:     { name: 'Sophia Institute',    search: 'https://sophiainstitute.com/search/?q={q}',        wrap: '', param: '', program: '20%: https://www.sophiainstitute.com/become-an-affiliate/' },
    wof:        { name: 'Word on Fire',        search: 'https://bookstore.wordonfire.org/search?q={q}',    wrap: '', param: '', program: '15%: https://bookstore.wordonfire.org/pages/affiliate-program' },
    baronius:   { name: 'Baronius Press',      search: 'https://www.baronius.com/?s={q}',                  wrap: '', param: '', program: 'no public program' },
    ics:        { name: 'ICS Publications',    search: 'https://www.icspublications.org/search?q={q}',     wrap: '', param: '', program: 'no public program' },
    avemaria:   { name: 'Ave Maria Press',     search: 'https://www.avemariapress.com/search?q={q}',       wrap: '', param: '', program: 'no public program' },
    scepter:    { name: 'Scepter',             search: 'https://scepterpublishers.org/search?q={q}',       wrap: '', param: '', program: 'no public program' },
    cluny:      { name: 'Cluny Media',         search: 'https://clunymedia.com/search?q={q}',              wrap: '', param: '', program: 'no public program' },
    angelico:   { name: 'Angelico Press',      search: 'https://angelicopress.com/search?q={q}',           wrap: '', param: '', program: 'no public program' },
    ascension:  { name: 'Ascension',           search: 'https://ascensionpress.com/search?q={q}',          wrap: '', param: '', program: 'no public program' }
  }
};
