from __future__ import annotations

TRUST_NAV_LINKS = [{'label': 'About', 'href': 'about.html'},
 {'label': 'Methodology', 'href': 'methodology.html'},
 {'label': 'Ethics', 'href': 'ethics.html'},
 {'label': 'Contact', 'href': 'contact.html'},
 {'label': 'Subscribe', 'href': 'subscribe.html'},
 {'label': 'Archive', 'href': 'archive.html'},
 {'label': 'RSS', 'href': 'feed.xml'}]

STATIC_PAGES = [{'slug': 'about',
  'output_name': 'about.html',
  'sitemap': True,
  'changefreq': 'monthly',
  'eyebrow': 'Open Source Signal / Trust pages',
  'title': 'About Open Source Signal',
  'title_uk': 'Про Сигнал відкритих джерел',
  'meta_description': 'Open Source Signal is a bilingual OSINT journal focused on Ukrainian '
                      'accountability OSINT, verification, tools, datasets, and investigative '
                      'workflows.',
  'lead': 'Open Source Signal / Сигнал відкритих джерел is a bilingual OSINT journal and digest '
          'focused on Ukrainian accountability OSINT.',
  'sections': [{'heading': 'English',
                'blocks': [{'type': 'p',
                            'text': 'Open Source Signal is not a general OSINT aggregator. It '
                                    'tracks open-source investigations, verification methods, '
                                    'datasets, tools, platform changes, and investigative '
                                    'workflows that matter for documenting harm, identifying '
                                    'responsible actors, understanding losses, captivity and '
                                    'missing-persons cases, and strengthening public-interest '
                                    'research.'},
                           {'type': 'p',
                            'text': 'Our editorial focus is Ukrainian accountability OSINT: '
                                    'open-source work that helps document harm, verify claims, '
                                    'preserve evidence, understand Russian military losses and '
                                    'captivity-related data, and explain the methods used by '
                                    'investigators, journalists, researchers, and civil-society '
                                    'groups.'},
                           {'type': 'ul',
                            'items': ['Ukrainian OSINT groups and investigators;',
                                      'war-crimes verification;',
                                      'identification and verification of Russian war-crime '
                                      'suspects;',
                                      'Russian KIA / POW / MIA / missing / wounded data;',
                                      'methods, datasets, ethics, OPSEC, and verification '
                                      'workflows;',
                                      'tools that help investigators work more carefully and '
                                      'safely.']},
                           {'type': 'p',
                            'text': 'The main editorial flow is English-language OSINT material '
                                    'adapted into Ukrainian for Ukrainian readers. When a strong '
                                    'source is Ukrainian-only, we do the reverse: we prepare an '
                                    'English editorial adaptation for international readers, '
                                    'preserving Ukrainian context and explaining institutions, '
                                    'terminology, and war-specific references.'},
                           {'type': 'p',
                            'text': 'Open Source Signal is a discovery layer, not a court, '
                                    'intelligence agency, or leak platform. We point to useful '
                                    'material, explain why it matters, describe how it can be '
                                    'used, and mark limits where verification is incomplete.'}]},
               {'heading': 'Українською',
                'blocks': [{'type': 'p',
                            'text': 'Сигнал відкритих джерел — це не загальний агрегатор '
                                    'OSINT-посилань. Наш фокус — українська accountability-оптика: '
                                    'відкриті джерела, розслідування, інструменти й методики, які '
                                    'допомагають документувати шкоду, перевіряти твердження, '
                                    'зберігати докази, розуміти дані про російські втрати, полон і '
                                    'зниклих безвісти.'},
                           {'type': 'ul',
                            'items': ['українські OSINT-групи й дослідники;',
                                      'верифікація воєнних злочинів;',
                                      'встановлення та перевірка осіб, причетних до злочинів;',
                                      'теми KIA / POW / MIA / missing / wounded щодо російських '
                                      'військових;',
                                      'методики, набори даних, етика, OPSEC і безпека дослідника;',
                                      'інструменти, які допомагають працювати точніше й '
                                      'обережніше.']},
                           {'type': 'p',
                            'text': 'Основний потік — англомовні OSINT-матеріали, які ми '
                                    'редакційно адаптуємо українською. Якщо важливе джерело існує '
                                    'лише українською, ми робимо зворотну операцію: готуємо '
                                    'англомовну редакційну адаптацію для міжнародної аудиторії.'},
                           {'type': 'p',
                            'text': 'Сигнал відкритих джерел не є судом, спецслужбою чи платформою '
                                    'для зливів. Ми допомагаємо знайти важливі матеріали, '
                                    'пояснюємо їхню цінність, показуємо межі застосування і не '
                                    'видаємо неперевірені дані за встановлені факти.'}]}],
  'cta_links': [{'label': 'Read the methodology', 'href': 'methodology.html'},
                {'label': 'Subscribe', 'href': 'subscribe.html'}]},
 {'slug': 'methodology',
  'output_name': 'methodology.html',
  'sitemap': True,
  'changefreq': 'monthly',
  'eyebrow': 'Open Source Signal / Trust pages',
  'title': 'Methodology',
  'title_uk': 'Методика',
  'meta_description': 'How Open Source Signal selects sources, verifies leads, adapts OSINT '
                      'material, handles risk, and separates public reporting from internal '
                      'editorial notes.',
  'lead': 'Open Source Signal is built around source discovery, editorial adaptation, verification '
          'awareness, and risk marking.',
  'sections': [{'heading': 'English',
                'blocks': [{'type': 'p',
                            'text': 'Each public card should help the reader understand what '
                                    'happened, why it matters, how it can be used, and where its '
                                    'limits are.'},
                           {'type': 'ul',
                            'items': ['rubric;',
                                      'title;',
                                      'source, date, and link;',
                                      'what happened;',
                                      'why it matters;',
                                      'how to use it;',
                                      'limits;',
                                      'tags.']},
                           {'type': 'p',
                            'text': 'We separate discovery from verification. Some sources are '
                                    'used as primary reporting or documentation. Others are used '
                                    'only as leads. Telegram channels, Reddit threads, community '
                                    'discussions, and newsletters can help discover tools, '
                                    'workflows, claims, or cases, but they do not automatically '
                                    'establish facts.'},
                           {'type': 'p',
                            'text': 'Tools and workflows found through newsletters or community '
                                    'discussions are checked against original project pages, '
                                    'GitHub repositories, documentation, author sites, release '
                                    'notes, or other primary references where possible.'},
                           {'type': 'p',
                            'text': 'For war-crimes verification, identity claims, POW / KIA / MIA '
                                    '/ missing-persons material, and suspect-related items, we '
                                    'apply a higher threshold. Telegram posts, Reddit comments, '
                                    'anonymous claims, or repost chains are not treated as '
                                    'established facts.'},
                           {'type': 'p',
                            'text': 'Every Daily Signal issue may contain an internal editorial '
                                    'block named EDITORIAL NOTES — INTERNAL. It is not part of the '
                                    'public cards and is used for editorial memory, safety '
                                    'cautions, weak-source notes, and weekly follow-up '
                                    'planning.'}]},
               {'heading': 'Discovery sources',
                'blocks': [{'type': 'p',
                            'text': 'OSINT Newsletter is used for tool discovery, workflow '
                                    'discovery, and Toolbox / Tool Radar candidates. Tools found '
                                    'through newsletters are checked against original project '
                                    'pages, GitHub repositories, documentation, or author sites.'},
                           {'type': 'p',
                            'text': 'Reddit OSINT communities are used as community radar and '
                                    'lead-only sources. They may help surface tools, workflows, '
                                    'questions, case ideas, or reading-list items. They are not '
                                    'used as proof for war crimes, identity claims, POW / KIA / '
                                    'MIA / missing-persons cases, or accusations against '
                                    'individuals.'},
                           {'type': 'p',
                            'text': 'Telegram sources are lead-only unless independently verified. '
                                    'Telegram can be useful for monitoring public narratives and '
                                    'discovering claims, but it is not treated as established '
                                    'fact.'},
                           {'type': 'p',
                            'text': 'Evocation.info is treated as a source pointer / database '
                                    'relevant to Ukrainian accountability OSINT. Because such '
                                    'databases may involve personal data, items derived from them '
                                    'require independent verification, risk review, and '
                                    'public-interest assessment.'}]},
               {'heading': 'Українською',
                'blocks': [{'type': 'p',
                            'text': 'Наша базова одиниця — редакційна картка. Вона має пояснювати, '
                                    'що сталося, чому це важливо, як матеріал можна використати і '
                                    'які обмеження треба враховувати.'},
                           {'type': 'p',
                            'text': 'Ми розділяємо виявлення сигналу і підтвердження факту. '
                                    'Telegram, Reddit, спільноти, розсилки й обговорення можуть '
                                    'допомогти знайти інструмент, кейс, методику або потенційний '
                                    'напрямок, але самі по собі не роблять твердження доведеним.'},
                           {'type': 'p',
                            'text': 'Для тем воєнних злочинів, ідентифікації осіб, POW / KIA / MIA '
                                    '/ missing, підозрюваних, командирів або колаборантів '
                                    'застосовується вищий поріг обережності.'}]}],
  'cta_links': [{'label': 'Ethics and safety', 'href': 'ethics.html'},
                {'label': 'Archive', 'href': 'archive.html'}]},
 {'slug': 'ethics',
  'output_name': 'ethics.html',
  'sitemap': True,
  'changefreq': 'monthly',
  'eyebrow': 'Open Source Signal / Trust pages',
  'title': 'Ethics and Safety',
  'title_uk': 'Етика й безпека',
  'meta_description': 'Editorial ethics, safety limits, source-risk policy, and publication '
                      'boundaries for Open Source Signal.',
  'lead': 'Open-source research can expose harm, but it can also create harm if handled '
          'carelessly.',
  'sections': [{'heading': 'English',
                'blocks': [{'type': 'p',
                            'text': 'Open Source Signal follows a public-interest, harm-aware '
                                    'approach.'},
                           {'type': 'p',
                            'text': 'We do not publish doxxing, private addresses, phone numbers, '
                                    'family details, personal contact data, credential hunting '
                                    'workflows, stolen data workflows, live targeting information, '
                                    'instructions that could help violence or unlawful access, '
                                    'unverified accusations presented as fact, or Telegram-only '
                                    'claims about war crimes, POWs, missing persons, or suspects '
                                    'without independent verification.'},
                           {'type': 'p',
                            'text': 'We may cover tools, datasets, investigations, and cases that '
                                    'involve sensitive topics. When doing so, we focus on '
                                    'methodology, public-interest value, verification status, and '
                                    'limits.'},
                           {'type': 'p',
                            'text': 'Telegram sources are treated as lead-only unless '
                                    'independently verified. Reddit OSINT communities are used as '
                                    'community radar and lead discovery, not as proof for war '
                                    'crimes, identity claims, POW / KIA / MIA / missing-persons '
                                    'cases, or accusations against individuals.'},
                           {'type': 'p',
                            'text': 'Evocation.info and similar databases can be relevant to '
                                    'Ukrainian accountability OSINT, but they require additional '
                                    'caution. If a database contains personal data, we apply risk '
                                    'review, independent comparison, and public-interest '
                                    'assessment before including it in public-facing material.'},
                           {'type': 'p',
                            'text': 'We avoid turning OSINT into spectacle. The goal is not viral '
                                    'exposure, but stronger documentation, verification, '
                                    'accountability, and safer investigative practice.'}]},
               {'heading': 'Українською',
                'blocks': [{'type': 'p',
                            'text': 'Сигнал відкритих джерел працює в логіці суспільного інтересу '
                                    'й мінімізації шкоди.'},
                           {'type': 'p',
                            'text': 'Ми не публікуємо doxxing, приватні адреси, телефони, сімейні '
                                    'дані, особисті контакти, workflow для credential hunting, '
                                    'stolen data, live targeting information, інструкції для '
                                    'насильства чи незаконного доступу, а також неперевірені '
                                    'звинувачення як встановлений факт.'},
                           {'type': 'p',
                            'text': 'Telegram-джерела вважаються lead-only, якщо немає незалежного '
                                    'підтвердження. Reddit OSINT-спільноти використовуються для '
                                    'пошуку інструментів, workflow, дискусій і потенційних кейсів, '
                                    'але не як доказ у чутливих темах.'},
                           {'type': 'p',
                            'text': 'Ми не перетворюємо OSINT на видовищне викриття заради самого '
                                    'викриття. Мета — документація, перевірка, відповідальність і '
                                    'безпечніша дослідницька практика.'}]}],
  'cta_links': [{'label': 'Methodology', 'href': 'methodology.html'},
                {'label': 'Subscribe', 'href': 'subscribe.html'}]},
 {'slug': 'contact',
  'output_name': 'contact.html',
  'sitemap': True,
  'changefreq': 'monthly',
  'eyebrow': 'Open Source Signal / Trust pages',
  'title': 'Contact',
  'title_uk': 'Зворотний зв’язок',
  'meta_description': 'Contact Open Source Signal with corrections, tips, tools, sources, and '
                      'editorial inquiries.',
  'lead': 'Send corrections, sources, tools, datasets, workflows, and public-interest tips. Do not '
          'send private personal data, credentials, stolen materials, or live targeting '
          'information.',
  'sections': [{'heading': 'Public mailboxes',
                'blocks': [{'type': 'link_list',
                            'items': [{'label': 'editor@osintsignal.org',
                                       'href': 'mailto:editor@osintsignal.org',
                                       'note': 'Corrections, editorial questions, attribution '
                                               'issues, and general inquiries.'},
                                      {'label': 'tips@osintsignal.org',
                                       'href': 'mailto:tips@osintsignal.org',
                                       'note': 'Public-interest leads, cases, datasets, '
                                               'investigations, and materials that may deserve '
                                               'review.'},
                                      {'label': 'tools@osintsignal.org',
                                       'href': 'mailto:tools@osintsignal.org',
                                       'note': 'OSINT tools, GitHub repositories, documentation, '
                                               'verification utilities, maps, archives, and '
                                               'datasets.'},
                                      {'label': 'sources@osintsignal.org',
                                       'href': 'mailto:sources@osintsignal.org',
                                       'note': 'Newsletters, Ukrainian OSINT projects, research '
                                               'groups, archives, Telegram monitoring candidates, '
                                               'and source suggestions.'}]},
                           {'type': 'p',
                            'text': 'Please do not send private addresses, phone numbers, family '
                                    'information, stolen credentials, non-public personal '
                                    'databases, malware, exploit material, live targeting '
                                    'information, or claims about identifiable people without '
                                    'source context.'}]},
               {'heading': 'Українською',
                'blocks': [{'type': 'p',
                            'text': 'Надсилайте виправлення, джерела, інструменти, датасети, '
                                    'workflow та суспільно важливі підказки. Не надсилайте '
                                    'приватні персональні дані, викрадені облікові дані, stolen '
                                    'materials або live targeting information.'}]}],
  'cta_links': [{'label': 'editor@osintsignal.org', 'href': 'mailto:editor@osintsignal.org'},
                {'label': 'tips@osintsignal.org', 'href': 'mailto:tips@osintsignal.org'},
                {'label': 'tools@osintsignal.org', 'href': 'mailto:tools@osintsignal.org'},
                {'label': 'sources@osintsignal.org', 'href': 'mailto:sources@osintsignal.org'}]},
 {'slug': 'subscribe',
  'output_name': 'subscribe.html',
  'sitemap': True,
  'changefreq': 'monthly',
  'eyebrow': 'Open Source Signal / Trust pages',
  'title': 'Subscribe',
  'title_uk': 'Підписка',
  'meta_description': 'Follow Open Source Signal through Telegram, RSS, and the public archive.',
  'lead': 'Follow Open Source Signal through Telegram, RSS, or the public archive.',
  'sections': [{'heading': 'Follow Open Source Signal',
                'blocks': [{'type': 'link_list',
                            'items': [{'label': 'Telegram',
                                       'href': 'https://t.me/open_source_signal_ua',
                                       'note': 'Announcements for new Daily Signal issues.'},
                                      {'label': 'RSS',
                                       'href': 'feed.xml',
                                       'note': 'Follow new issues in any feed reader.'},
                                      {'label': 'Archive',
                                       'href': 'archive.html',
                                       'note': 'Browse previous Daily Signal issues.'}]},
                           {'type': 'p',
                            'text': 'Daily Signal is published Monday to Friday when there is '
                                    'enough material worth surfacing.'}]},
               {'heading': 'Українською',
                'blocks': [{'type': 'p',
                            'text': 'Підписатися можна через Telegram, RSS або архів сайту.'}]}],
  'cta_links': [{'label': 'Telegram', 'href': 'https://t.me/open_source_signal_ua'},
                {'label': 'RSS', 'href': 'feed.xml'},
                {'label': 'Archive', 'href': 'archive.html'}]}]

NOT_FOUND_PAGE = {'slug': '404',
 'output_name': '404.html',
 'sitemap': False,
 'eyebrow': 'Open Source Signal / Error',
 'title': 'Signal lost',
 'title_uk': 'Сигнал не знайдено',
 'meta_description': 'The requested page could not be found.',
 'lead': 'The signal you requested is not here.',
 'body_en': 'The page may have moved, the link may be broken, or the issue may not exist. You can '
            'return to the latest Daily Signal, browse the archive, or follow the project through '
            'Telegram and RSS.',
 'body_uk': 'Сторінку могли перенести, посилання могло зламатися, або такого випуску не існує. '
            'Можна повернутися на головну, переглянути архів або підписатися через Telegram чи '
            'RSS.',
 'cta_links': [{'label': 'Latest signal', 'href': 'index.html'},
               {'label': 'Archive', 'href': 'archive.html'},
               {'label': 'Telegram', 'href': 'https://t.me/open_source_signal_ua'},
               {'label': 'RSS', 'href': 'feed.xml'}]}
