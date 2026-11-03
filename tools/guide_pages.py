"""HTML for the help guides under /guides/ (steering C, 2026-11-03). One source for the app (data/guides.js,
written by tools/build_guides.py) and the static pages (tools/build_static.py).

Rules for this file (tests/test_epub_guide.py checks them):
- Every step is checked against the vendor's own help page, and each section cites that page. Do not invent menu
  names: if a vendor page does not name a button, describe the step without one.
- No shopping or affiliate links of any kind. Amazon links are allowed only to Amazon help pages and the Send to
  Kindle pages (amazon.com/gp/help/... and amazon.com/sendtokindle...); never a product page.
- No em-dashes, Oxford commas, no analytics attributes (data-support, data-ga, onclick).
- No in-page #anchor links: the app reads any hash as a route.
- Do not favor EPUB over the reading room: the guide opens by saying the reading room needs no download.
CHECKED is the date the vendor pages were last read."""
from html import escape as E
CHECKED='2026-11-03'
SOURCES={
 'stk':('Amazon Help: Send PDF, EPUB and Other Files to Your Kindle','https://www.amazon.com/gp/help/customer/display.html?nodeId=G5WYD9SAF7PGXRNA'),
 'stk_email_help':('Amazon Help: Send to Kindle by email','https://www.amazon.com/gp/help/customer/display.html?nodeId=G7NECT4B4ZWHQ8WV'),
 'stk_email':('Amazon: Send to Kindle by email','https://www.amazon.com/sendtokindle/email'),
 'stk_ios':('Amazon: Send to Kindle from iPhone and iPad','https://www.amazon.com/sendtokindle/ios'),
 'stk_android':('Amazon: Send to Kindle from Android','https://www.amazon.com/sendtokindle/android'),
 'kindle_usb':('Amazon Help: Connect, Browse, and Transfer Files on E-Reader','https://www.amazon.com/gp/help/customer/display.html?nodeId=TCUBEdEkbIhK07ysFu'),
 'kobo':('Kobo Help: Add eBooks to your Kobo eReader using your computer','https://help.kobo.com/hc/en-us/articles/360024775093'),
 'apple_mac':('Apple Books User Guide: Import books, audiobooks, or PDFs in Books on Mac','https://support.apple.com/guide/books/import-books-audiobooks-or-pdfs-ibkseed72068/mac'),
 'apple_iphone':('iPhone User Guide: Read PDF documents in the Books app on iPhone','https://support.apple.com/guide/iphone/iphab2193d5/ios'),
 'play_books':('Google Play Books Help: Upload files to Google Play Books','https://support.google.com/googleplay/answer/11012086'),
 'moon':('Moon+ Reader on Google Play','https://play.google.com/store/apps/details?id=com.flyersoft.moonreader'),
 'calibre':('calibre User Manual: The graphical user interface','https://manual.calibre-ebook.com/gui.html'),
}
def src(*keys):
    return '<p class="small guide-source">Checked '+CHECKED+' against '+', '.join('<a href="'+E(SOURCES[k][1])+'" target="_blank" rel="noopener">'+E(SOURCES[k][0])+' ↗</a>' for k in keys)+'.</p>'
def ol(*steps):return '<ol>'+''.join('<li>'+s+'</li>' for s in steps)+'</ol>'
def epub_html():
    return ('<div class="guide-page"><div class="page-head"><div class="eyebrow">Guides</div><h1>Read an EPUB on your device</h1>'
     '<p class="lede">How to put a free EPUB file from this library on a Kindle, a Kobo, an iPhone or iPad, an Android phone or tablet, or a computer, in plain steps.</p></div>'
     '<section class="panel policy">'
     '<p class="notice"><b>You may not need a download at all.</b> Every text in the <a href="/library/">Reading Room</a> opens right in your web browser, on any phone, tablet, or computer, with nothing to install. Use an EPUB when you want the book on an e-reader or offline.</p>'
     '<p>EPUB is a common ebook format. The EPUB files linked from this library come from the original digital libraries, such as Project Gutenberg, and are offered only for books that are in the public domain in the United States. These steps are for files without copy protection (DRM). Download the file first, then follow the steps for your device.</p>'
     '<p class="small">Sections: Kindle, Kobo, Apple Books on Mac, iPhone, and iPad, Android phones and tablets, Calibre on a computer, and PDF.</p>'
     '<h2 id="kindle">Kindle</h2>'
     '<p>Amazon’s Send to Kindle service accepts EPUB files and adds them to your Kindle library, where they open on your Kindle e-reader and in the Kindle app. Choose one of these ways.</p>'
     '<h3>By email</h3>'+ol(
       'Find your Send to Kindle email address. Amazon lists it under Manage Your Content and Devices, then Preferences, then Personal Document Settings.',
       'In the same place, add the email address you will send from to your Approved Personal Document Email List.',
       'Email the EPUB to your Send to Kindle address as an attachment. You do not need a subject line.',
       'Wait for the book to arrive in your Kindle library, then open it on your Kindle or in the Kindle app.')+
     '<p class="small">Amazon’s limits: up to 25 attachments and 50 MB per email, and up to 15 approved email addresses.</p>'
     '<h3>In a web browser</h3>'+ol(
       'Go to <a href="https://www.amazon.com/sendtokindle" target="_blank" rel="noopener">amazon.com/sendtokindle</a> and sign in with your Amazon account.',
       'Drag the EPUB onto the page, or select it from your computer. Files can be up to 200 MB.',
       'Make sure “Add to your library” is turned on so the book stays in your Kindle library, then send it.')+
     '<h3>From the Kindle app on a phone or tablet</h3>'+ol(
       'Install or update the Kindle app on your iPhone, iPad, or Android device.',
       'Open the downloaded EPUB file and tap the Share icon.',
       'Choose Kindle from the sharing options.')+
     '<h3>From a computer app</h3><p>Amazon also offers a Send to Kindle app for Mac and for Windows that sends files to your Kindle library.</p>'
     '<h3>With a USB cable</h3>'
     '<p>Amazon recommends sending files wirelessly with Send to Kindle, and that is the way to use for an EPUB, because Send to Kindle prepares the file for your Kindle. A cable is handy for a PDF:</p>'+ol(
       'Connect the Kindle to your computer with a USB cable. On Windows it appears in File Explorer as a drive named Kindle.',
       'Copy the file into the Kindle’s “Documents” folder, then eject the Kindle before unplugging it.')+
     '<p class="small">On a Mac, Amazon says Kindle Scribe and Kindle models released in 2024 or later need the Send to Kindle app for Mac to move files by cable; its Tools menu has a USB File Manager.</p>'
     +src('stk','stk_email_help','stk_email','stk_ios','stk_android','kindle_usb')+
     '<h2 id="kobo">Kobo</h2>'+ol(
       'Connect your Kobo eReader to your computer with a USB cable, and tap Connect on the eReader.',
       'On your computer, open the drive named KOBOeReader.',
       'Drag the EPUB file onto the KOBOeReader drive.',
       'Eject the eReader from your computer, then unplug the cable. The Kobo shows “Importing content” and then the book appears in your library.')+
     '<p class="small">Kobo also explains how to add files from Google Drive or Dropbox. Books added this way appear only on that eReader.</p>'
     +src('kobo')+
     '<h2 id="apple">Apple Books on Mac, iPhone, and iPad</h2>'
     '<h3>On a Mac</h3>'+ol(
       'Open the Books app.',
       'Choose File, then Import.',
       'Select the EPUB file, then click Import. You can also drag the file into your Books library.')+
     '<p class="small">Apple says Books can import many EPUB books. With iCloud for Books turned on, books you import can also appear on your other Apple devices.</p>'
     '<h3>On an iPhone or iPad</h3>'+ol(
       'Open the downloaded file, for example from the Files app or from an email.',
       'Tap the Share button, then tap Books.')+
     '<p class="small">Apple’s iPhone guide describes these steps for PDFs you receive in Mail, Messages, or other apps; an EPUB file is opened in Books from the Share button in the same way.</p>'
     +src('apple_mac','apple_iphone')+
     '<h2 id="android">Android phones and tablets</h2>'
     '<h3>Google Play Books</h3>'+ol(
       'Open the downloaded EPUB from your Downloads or Files app.',
       'Choose to open it with Play Books, or upload it to Play Books.',
       'Find the book in the Play Books app under Library, then Uploads.')+
     '<p>You can also upload from a computer: open Play Books in a web browser, go to Your books, select Upload files, and choose the EPUB. Uploaded books appear under Uploads.</p>'
     +src('play_books')+
     '<h3>Moon+ Reader</h3>'
     '<p>Moon+ Reader is an Android reading app that opens EPUB and PDF files. Install it from Google Play, then use its file browser to open the EPUB from your Downloads folder, or add the file to its bookshelf. Its Google Play listing notes that it contains ads and in-app purchases. We are not affiliated with it.</p>'
     +src('moon')+
     '<h2 id="calibre">Calibre on a computer</h2>'
     '<p>Calibre is a free ebook manager for Windows, Mac, and Linux. It can keep your EPUB files in one library, convert them, and copy them to many e-readers.</p>'+ol(
       'Click Add books and choose the EPUB file.',
       'To use the book on a reader that needs another format, select it and click Convert books.',
       'Connect your e-reader with a USB cable, select the book, and click Send to device. Eject the device in Calibre before unplugging it.')+
     '<p class="small">Calibre does not convert books with copy protection (DRM).</p>'
     +src('calibre')+
     '<h2 id="pdf">Prefer a PDF?</h2>'
     '<p>A PDF keeps the printed page layout, opens on almost any phone, tablet, or computer, and can be printed; an EPUB reflows its text to fit small screens. Some works also have a PDF edition: a work’s “Other formats” section points to the St. Isidore Library catalog in the <a href="/isidore/">Isidore Index</a>, and an Index record shows download buttons only when its rights badge allows them. You can always read a hosted text in the <a href="/library/">Reading Room</a> with no download.</p>'
     '<p class="small">These steps come from each company’s own help pages, checked on '+CHECKED+'. Menus change from time to time; if a step does not match what you see, follow the linked help page. Bibliotheca Catholica is not affiliated with Amazon, Kobo, Apple, Google, Moon+ Reader, or calibre.</p>'
     '</section></div>')
PAGES={'epub-on-your-device':{'title':'Read an EPUB on your device','desc':'How to put a free EPUB from this library on a Kindle, Kobo, iPhone, iPad, Android device, or computer, with steps checked against each company’s help pages.','html':None}}
def pages():
    PAGES['epub-on-your-device']['html']=epub_html();return PAGES
