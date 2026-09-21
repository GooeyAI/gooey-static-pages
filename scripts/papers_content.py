"""Text of the /research papers, extracted from the hosted PDFs.

Edit here, then run scripts/build_papers.py to regenerate the pages.

`listed_as` must match the paper's `title` in the Google Sheet exactly — that is
how a row in the papers list finds its page.

Block kinds:  ("p", text) ("h3", text) ("ul", [items]) ("fig", n, caption)
              ("q", quote, attribution)
Inline marks: **strong**, *emphasis*, [label](https://url)
"""

RCA = "Royal College of Art"
GOOEY = "Gooey.AI"

AUTHORS_RCA = [
    ("Archana Prasad", RCA, "archana.prasad@network.rca.ac.uk"),
    ("Isha Singh", GOOEY, "isha@gooey.ai"),
    ("Tom Simmons", RCA, "tom.simmons@rca.ac.uk"),
]

PAPERS = [
    # ---------------------------------------------------------------- CHI 2026
    {
        "slug": "ai-across-cultures-shaping-ai",
        "listed_as": "AI Across Cultures: Shaping AI",
        "title": "Shaping AI: Ethics, Power, and Responsibility",
        "status": "Preprint",
        "authors": AUTHORS_RCA,
        "abstract": (
            "This paper examines how AI is subtly shaped by racist undertones and "
            "perpetuates bias. It presents an overview of the roundtable Shaping AI, "
            "held in New Delhi in December 2025, which brought together community "
            "journalists to probe the overt and covert forms of racism they encounter "
            "in their professional lives and in their interactions with AI systems. "
            "The paper further explores how large language models can be shaped and "
            "trained to enable greater inclusivity and representation, while actively "
            "combating racial bias."
        ),
        "meta": [
            ("CCS Concepts", [
                "Computing methodologies → Artificial intelligence",
                "Human-centered computing → Collaborative and social computing",
                "Social and professional topics → Race and ethnicity",
            ]),
            ("Keywords", [
                "Artificial intelligence, racism, bias, large language models, "
                "inclusive AI, journalism, Global South"
            ]),
        ],
        "sections": [
            {
                "num": "1",
                "id": "broader-context",
                "title": "The Broader Context",
                "blocks": [
                    ("p", "Imagine you're a young girl in rural Uttar Pradesh and your access to a smartphone is mediated entirely through your brother's phone. Your everyday life is shaped by entrenched gendered bias and explicit prohibitions from local power authorities known as khap panchayats that restrict the use of phones for girls. You encounter racism daily but have no safe spaces to process your experiences with this systemic issue. Meanwhile, your urban, formally educated peers not only use smartphones but engage with AI tools with ease, thus shaping who gets access to new technologies."),
                    ("p", "In a world where the rise of AI tools has meant that there are millions of people using AI to learn, upskill or pivot their careers or lives, the burdens of caste, gender and geographic location mean that being excluded from this and similar emerging technologies is a lived reality for many. While AI has the potential to democratise storytelling, existing social hierarchies are also reproduced and intensified through unequal access and representation to digital technologies and shaping the underlying data that drives them."),
                    ("fig", 1, "Figure 1: Participants gathered for the roundtable discussion"),
                    ("p", "Racism, an inherent part of societal structures and cultures, including design, also risks getting reflected in AI tools which may unintentionally perpetuate these biases. As Sasha Costanza-Chock argues, universalist design practices tend to erase intersectionally disadvantaged groups by assuming a 'neutral' user that does not exist [1]. In fact, a 2024 study published in Nature found that AI language models discriminate between people based on their dialects, as they mirror known human prejudices [2]."),
                    ("p", "This white paper examines a two-day roundtable in Delhi, held on 2–3 December 2025, that sought to address these challenges. The event was a collaborative initiative supported by the Goethe-Institut New Delhi, India, The Federal Agency for Civic Education (BpB) in Germany and Gooey.AI."),
                    ("p", "The roundtable's central aim was to identify how racism impacts AI participation in India, and how AI systems reinforce existing biases, alongside developing mitigating strategies for equal access to AI."),
                ],
            },
            {
                "num": "2",
                "id": "structural-barriers",
                "title": "Structural Barriers and Societal Challenges in Indian Society",
                "blocks": [
                    ("p", "The roundtable featured 16 journalists from community media organizations like Chambal Media and Video Volunteers, with many representing marginalized communities themselves. These journalists were chosen for their engagement with rural, underrepresented populations in Uttar Pradesh, Madhya Pradesh, Rajasthan and other states across the country. Participants highlighted entrenched gender, caste, and class hierarchies that hinder access to AI technology."),
                    ("p", "During the roundtable, participants shared common experiences which included constrained access to mobile devices and the internet for women, often controlled by male members of the family. They also discussed that women and marginalized individuals faced negative social perceptions for engaging with technology, often being told that their pictures would get “morphed” and misused by AI tools. This would further exacerbate fears around AI, thus leading to self-limited exposure to emerging tech. In a vicious disruptive cycle, these constraints lead to rural and underserved communities being further excluded from AI and wealthy, urbane and largely global north tech organisations gaining unfair and unequal narrative control on representation. In fact, seeing that LLMs did not have much Icelandic data, the government of Iceland decided the best option was to give OpenAI extensive Icelandic language resources to improve model accuracy [3]."),
                    ("p", "As a diverse population, India has various linguistic, social and cultural groups which are unrepresented or misrepresented or simply ignored entirely in AI training data, with the looming threat of erasure. As AI gets more fluent in dominant languages and power structure, the generated content fails to represent these rural communities. As successive Large Language Models (LLMs) are trained on these biased foundational datasets, bias is recursively accumulated, progressively amplifying and entrenching systemic inequalities over time. As Chen et al. argue, “If the data used to train the model are not representative of the population, or if certain groups are underrepresented or excluded in the data, then biases are likely to exist in collection and preparation of the data” [4]."),
                    ("p", "To address these gaps, the roundtable aimed to expand participation in AI development by amplifying underrepresented voices in AI storytelling. Participants were invited to actively shape the direction, insights, and design of AI training processes, grounding these interventions in the lived realities of gender- and caste-based discrimination in order to confront systemic exclusion and contribute to the creation of more culturally attuned datasets."),
                ],
            },
            {
                "num": "3",
                "id": "roundtable-design",
                "title": "Roundtable Design and Methodology",
                "blocks": [
                    ("p", "As the roundtable foregrounded community participation and interrogated the complex dynamics of racism embedded within technological systems, it adopted a community-centred, participatory methodology. Journalists from two rural media organisations were brought together to exchange experiences grounded in their local contexts. Participants were introduced to AI tools for creative practice and critically exposed to the ways in which AI training data can be exclusionary or biased. This need was further underscored by a Thomson Reuters Foundation survey indicating that 57.6% of journalists are self-taught in AI, highlighting a significant gap in structured AI training [5]."),
                    ("p", "When even urban journalists in the Global Majority lack access to meaningful AI training, the idea that such knowledge will organically trickle down to rural newsrooms is an illusion. The roundtable's engagement with underrepresented populations was intentional in tackling this nonlinear knowledge diffusion of AI technology."),
                    ("p", "We structured the roundtable into the following key activities:"),
                    ("ul", [
                        "**Story Sharing and Reflection Sessions:** The participants shared their experiences of caste, gender and class-based racism and how covert racism reflects in their professional lives.",
                        "**Digging Deeper, Huddles, and Blue-Sky Speculations on AI Futures:** These deep-dives allowed participants to explore how racism manifests in AI systems and what kind of strategies are needed to design more inclusive, context-aware AI tools.",
                        "**Hands-on Practices with the Model Image and Video Trainer Tools:** Gooey.AI, as the driving tech force behind this initiative had created a Model Image Trainer Tool as well as a Video Generation tool. To create more equitable access to tech and to solve the language barrier, we created an AI agent which participants could use to speak in Hindi and generate prompts for the tools in English. Using the AI tools, participants trained their model trainer in their unique, aesthetic styles thus experimenting with narrative generation and image and video creation. Our digital interventions confronted UX challenges for non-English speakers and instilled confidence in them regarding AI.",
                    ]),
                    ("fig", 2, "Figure 2: Participants noting down their thoughts during a group exercise"),
                    ("ul", [
                        "**Peer Learning and Support:** We devised the roundtable in a way that participants could form cross-sector networks and connect beyond the project as well. This was meant to sustain collaboration and community-driven AI development.",
                        "**An AI Curriculum for Journalists:** In order to bridge the data divide between AI users and rural communities with no access to AI, we used methods like reverse ideations and core huddles to create an AI curriculum for journalists from marginalised communities.",
                    ]),
                ],
            },
            {
                "num": "4",
                "id": "recommendations",
                "title": "Recommendations",
                "blocks": [
                    ("p", "The imbalance within AI is not incidental but a structural flaw from bias in training data and non-inclusive systems and infrastructures design. As Dr. Katelyn Jones observes: 95 percent of images used to train AI models depict white skin, while medical algorithms often draw on U.S. military datasets in which women may constitute only six percent of subjects [6]."),
                    ("p", "The AI Now Institute notes, “claims of objectivity and neutrality in AI systems often mask underlying power relations and systemic biases embedded in the data and the institutions that produce it” [7]. This shocking statistic highlights what we have known all this while: data merely masquerades as objective while being riddled with biases. The centrality of community and creative participation thus becomes paramount and this roundtable was a small but important step towards that process. From the learnings at the roundtable, we gleaned the following recommendations:"),
                    ("ul", [
                        "**Establishing a safe context for AI training for Journalists from Rural Communities:** It is imperative to create safe and financially supported spaces for women and other journalists from marginalised communities to experiment with AI and express themselves creatively. Our roundtable provided a space to a cohort of journalists to create images and videos in their creative styles, centering their everyday experiences and cultural contexts.",
                    ]),
                    ("fig", 3, "Figure 3: Cultural and context-aware outputs from our model image trainer — a contemporary Mughal-miniature style depiction of women on a motorbike and a journalistic avatar"),
                    ("ul", [
                        "**Anti-Racist AI Practices:** The roundtable delved deep into the question of what constitutes an anti-racist AI. Can an AI which is shaped by the biases of contemporary society be changed and made anti-racist by formulating legal frameworks? Or do we need different kinds of AI systems, which are the “utopian” versions of present AI from big tech? How can underrepresented voices be empowered in AI participation so that present-day AI is trained better and we also work towards an inclusive, sustainable AI for good? As Dancy and Saucier contend, focusing merely on bias in AI is insufficient and we must move towards examining the “design, development and deployment of AI systems” and cultures [8]. An anti-racist AI would reflect linguistic and cultural diversity and prevent cultural misappropriation. During the roundtable, participants observed how they could find stereotypes about their region, and gender in AI generated news content.",
                        "**Capacity Building Exercises for Digital Confidence:** The hands-on exercises with Gooey tools demonstrated that participants could build AI confidence even without prior knowledge of AI. For this, we need tools which are tailored for different contexts. By creating an AI agent for Image Prompting, Gooey helped non-English speakers use the tools with ease.",
                        "**Mitigating Biases in AI Systems through AI Literacy:** The roundtable showed that learning AI enabled storytelling allowed participants to engage more closely with algorithmic biases and relate them with their lived experiences. This turned their focus towards developing mitigating strategies like an AI curriculum for their peers and brainstorming on ethical frameworks for AI. Participants also viewed AI through a feminist lens, noting how it has stereotypes about what Indian women should look like. An AI generated image of an Indian woman had long dark hair, was clad in a kurta set and wore a bindi. Participants who were dressed differently from this AI representation and in varied ways understood the importance of creating AI images rooted in their personal and cultural narratives.",
                        "**Tool Iterations and Ethical Frameworks for an Inclusive AI:** The Gooey Model Image Trainer is designed in a way that it can be iterated with participant feedback. Following the roundtable, the Gooey team incorporated participant feedback and turned the image trainer tool into an AI agent which works on WhatsApp. The roundtable also brought fresh perspectives on ethical frameworks for safe and practical engagement with AI, like ensuring data privacy, attribution, and culturally sensitive use of AI outputs.",
                    ]),
                ],
            },
            {
                "num": "5",
                "id": "concluding-remarks",
                "title": "Concluding Remarks",
                "blocks": [
                    ("p", "The Shaping AI roundtable unearthed how AI surfaces racist stereotypes and linked it to everyday realities of gender and caste based discrimination. It demonstrated how inclusive AI design needs to be intentional and participatory. While big tech firms use training data for fine-tuning their AI models, they do not collaborate with marginalized communities to truly erase biases or minimize them. This gap opens up the possibilities for open-source models which can be developed to be more culturally sensitive and nuanced through greater collaboration and transparency."),
                    ("p", "“Designing for ethical and inclusive AI refers to the intentional incorporation of human worth, autonomy, and identity into the fabric of AI systems” [9]. This roundtable showed that with intent, organisations can create spaces for pilot projects and training for AI, center lived experiences and reflect diverse cultural perspectives in AI. To commit to an AI that is inclusive, anti-racist and equitable for all, organisations and policymakers need long-term community engagement. So that one day, a girl from a marginalized community in rural Uttar Pradesh can create an AI news anchor in her likeness rather than a white one, to report stories from her region, in her voice."),
                ],
            },
            {
                "id": "acknowledgments",
                "title": "Acknowledgments",
                "cls": "tight",
                "blocks": [
                    ("p", "We thank the community journalists from Chambal Media and Video Volunteers for sharing their insights with us. We would also like to thank the Goethe-Institut New Delhi, and the Federal Agency for Civic Education (BpB), for their support."),
                ],
            },
            {
                "id": "references",
                "title": "References",
                "cls": "ruled refs",
                "blocks": [
                    ("ul", [
                        "Sasha Costanza-Chock. 2018. Design justice, A.I., and escape from the matrix of domination. *Journal of Design and Science*, 3. MIT Press. [jods.mitpress.mit.edu](https://jods.mitpress.mit.edu/pub/costanza-chock/release/4)",
                        "Valentin Hofmann, Pratyusha Ria Kalluri, Dan Jurafsky, et al. 2024. AI generates covertly racist decisions about people based on their dialect. *Nature* 633 (2024), 147–154. [doi.org/10.1038/s41586-024-07856-5](https://doi.org/10.1038/s41586-024-07856-5)",
                        "Anya Schiffrin. n.d. AI and the future of journalism: An issue brief for stakeholders. *World Trends in Freedom of Expression and Media Development*. UNESCO.",
                        "You Chen, Ellen Wright Clayton, Laurie Lovett Novak, Shilo Anders, and Bradley Malin. 2023. Human-centered design to address biases in artificial intelligence. *Journal of Medical Internet Research* 25 (2023).",
                        "Damian Radcliffe. 2025. Journalism in the AI era: Opportunities and challenges in the Global South and emerging economies. *Thomson Reuters Foundation Insights Report*. [trust.org](https://www.trust.org/wp-content/uploads/2025/01/TRF-Insights-Journalism-in-the-AI-Era.pdf)",
                        "Katelyn Jones and Nicole Mattea. 2020. We need a feminist approach to AI development. *Women in International Security (WIIS Global)*, June 5, 2020. [wiisglobal.org](https://wiisglobal.org/we-need-a-feminist-approach-to-ai-development/)",
                        "S. M. West, M. Whittaker, and K. Crawford. 2019. Discriminating systems: Gender, race, and power in AI. *AI Now Institute*. [ainowinstitute.org](https://ainowinstitute.org/publications/discriminating-systems-gender-race-and-power-in-ai-2)",
                        "Christopher L. Dancy and P. Khalil Saucier. 2021. AI and Blackness: Toward moving beyond bias and representation. *IEEE Transactions on Technology and Society* PP, 99 (2021), 1–1. [doi.org/10.1109/TTS.2021.3125998](https://doi.org/10.1109/TTS.2021.3125998)",
                        "Anushree Jain. 2025. Designing for ethical and inclusive AI through a human-centered design lens. *Global Business & Economics Journal*, June 5, 2025. [gbej.org](https://gbej.org/articles/designing-for-ethical-and-inclusive-ai-through-a-human-centered-design-lens/)",
                    ]),
                ],
            },
            {
                "id": "appendix",
                "title": "Appendix: Participant Perspectives",
                "cls": "ruled",
                "blocks": [
                    ("p", "Several participants highlighted the importance of creating safe learning environments for AI like the Shaping AI roundtable, which was a critical step towards a more inclusive, anti-racist AI designed in participatory ways."),
                    ("q", "We could make AI better by providing a space to learn safely while still protecting personal art and its equivalent. It shifts power as creators and communities get to decide how to share and protect their culture and stories.", "Nidhi Thachankary, Chief Business Officer, Chambal Academy"),
                    ("p", "Others drew attention to the representation gap within AI ecosystems, particularly for organizations like Chambal Media working at the intersections of gender, caste, and class."),
                    ("q", "As an organization which works with marginalized communities, and understands gender, caste, class in a much deeper way, we feel a huge gap when it comes to AI. The targeted audiences are also very different. What we need in this technology space is to make it more inclusive and to have more representation.", "Priya Thuvassery, Co-CEO, Chambal Media"),
                ],
            },
        ],
    },

    # ------------------------------------------------- Art of Research 2026
    {
        "slug": "shaping-ai-ethics-power-and-responsibility",
        "listed_as": "Shaping AI: Ethics, Power and Responsibility",
        "title": "Shaping AI: Ethics, Power and Responsibility",
        "status": "Art of Research 2026: Voices",
        "authors": AUTHORS_RCA,
        "abstract": (
            "This paper examines how AI is subtly shaped by racist undertones and "
            "perpetuates bias. It presents an overview of the roundtable Shaping AI, "
            "held in New Delhi in December 2025, which brought together community "
            "journalists to probe the overt and covert forms of racism they encounter "
            "in their professional lives and in their interactions with AI systems. "
            "The paper further explores how large language models can be shaped and "
            "trained to enable greater inclusivity and representation, while actively "
            "combating racial bias. By countering algorithmic silencing using listening "
            "and polyphonic systems, we can move towards more inclusive AI."
        ),
        "meta": [
            ("Keywords", ["Artificial intelligence, bias, inclusive AI"]),
            ("Published in", [
                "Art of Research 2026: Voices, ISSN 2984-0724. Licensed under a "
                "Creative Commons Attribution-NonCommercial 4.0 International Licence."
            ]),
        ],
        "sections": [
            {
                "num": "1",
                "id": "introduction",
                "title": "Introduction",
                "blocks": [
                    ("p", "Imagine you're a young girl in rural Uttar Pradesh and your access to a smartphone is mediated entirely through your brother's phone. Your everyday life is shaped by entrenched gendered bias and explicit prohibitions from local power authorities known as khap panchayats that restrict the use of phones for girls. You encounter racism daily but have no safe spaces to process your experiences with this systemic issue. Meanwhile, your urban, formally educated peers not only use smartphones but engage with AI tools with ease, thus shaping who gets access to new technologies."),
                    ("p", "In a world where the rise of AI tools has meant that there are millions of people using AI to learn, upskill or pivot their careers or lives, the burdens of caste, gender and geographic location mean that being excluded from this and similar emerging technologies is a lived reality for many. While AI has the potential to democratise storytelling, existing social hierarchies are also reproduced and intensified through unequal access and representation to digital technologies and shaping the underlying data that drives them."),
                    ("fig", 1, "Figure 1: Participants gathered for the roundtable discussion"),
                    ("p", "Racism, an inherent part of societal structures and cultures, including design, also risks getting reflected in AI tools which may unintentionally perpetuate these biases. As Sasha Costanza-Chock argues, universalist design practices tend to erase intersectionally disadvantaged groups by assuming a 'neutral' user that does not exist (Costanza-Chock 2018). In fact, a 2024 study published in Nature found that AI language models discriminate between people based on their dialects, as they mirror known human prejudices (Hofmann et al. 2024)."),
                    ("p", "This study examines a two-day roundtable in Delhi, held on 2–3 December 2025, that sought to address these challenges. The event was a collaborative initiative supported by the Goethe-Institut New Delhi, India, The Federal Agency for Civic Education (BpB) in Germany and an AI platform."),
                    ("p", "The roundtable's central aim was to identify how racism impacts AI participation in India, and how AI systems reinforce existing biases, alongside developing mitigating strategies for equal access to AI. By using the roundtable as a focal point, this paper argues for polyphonic, dialogic and context-sensitive AI systems as the need of the hour."),
                ],
            },
            {
                "num": "2",
                "id": "structural-barriers",
                "title": "Structural Barriers and Societal Challenges in Indian Society",
                "blocks": [
                    ("p", "The roundtable featured 16 journalists from community media organizations like Chambal Media and Video Volunteers, with many representing marginalized communities themselves. Both these organisations work to empower community voices within journalism. These journalists were chosen for their engagement with rural, underrepresented populations in Uttar Pradesh, Madhya Pradesh, Rajasthan and other states across the country. Participants highlighted entrenched gender, caste, and class hierarchies that hinder access to AI technology, in the rural hinterlands of India."),
                    ("p", "During the roundtable, participants shared common experiences which included constrained access to mobile devices and the internet for women, often controlled by male members of the family. They also discussed that women and marginalized individuals faced negative social perceptions for engaging with technology, often being told that their pictures would get “morphed” and misused by AI tools. This would further exacerbate fears around AI, thus leading to self-limited exposure to emerging tech."),
                    ("p", "In a vicious disruptive cycle, these constraints lead to rural and underserved communities being further excluded from AI and wealthy, urbane and largely Global North tech organisations gaining unfair and unequal narrative control on representation. In fact, as LLMs did not have much Icelandic data, the government of Iceland decided the best option was to give OpenAI extensive Icelandic language resources to improve model accuracy (Schiffrin n.d.)."),
                    ("p", "These exclusions are not merely a matter of access but of voice – who gets silenced and who is heard within big tech systems. Dominant, western-centric data is in fact, a form of systemic injustice which legitimises certain cultures and voices while suppressing others. The subtheme of Silencing for this conference is very much relevant here. In the case of AI, silencing operates at multiple levels – absence of training datasets, lack of access to AI tools and lack of linguistic representation. While big tech incorporates more languages into its AI systems, these systems are often not adequately trained on diverse languages, leading to incorrect responses. This leads to entire communities being erased or misrepresented within AI systems."),
                    ("p", "As a diverse population, India has various linguistic, social and cultural groups which are unrepresented or misrepresented or simply ignored entirely in AI training data, with the looming threat of erasure. As AI gets more fluent in dominant languages and power structures, the generated content fails to represent these rural communities. As successive Large Language Models (LLMs) are trained on these biased foundational datasets, bias is recursively accumulated, progressively amplifying and entrenching systemic inequalities over time. As Chen et al. argue, “If the data used to train the model are not representative of the population, or if certain groups are underrepresented or excluded in the data, then biases are likely to exist in the collection and preparation of the data” (Chen et al. 2023)."),
                    ("p", "To address these gaps, the roundtable aimed to expand participation in AI development by amplifying underrepresented voices in AI storytelling. Participants were invited to actively shape the direction, insights, and design of AI training processes, grounding these interventions in the lived realities of gender- and caste-based discrimination in order to confront systemic exclusion and contribute to the creation of more culturally attuned datasets."),
                ],
            },
            {
                "num": "3",
                "id": "roundtable-design",
                "title": "Roundtable Design and Methodology",
                "blocks": [
                    ("p", "As the roundtable foregrounded community participation and interrogated the complex dynamics of racism embedded within technological systems, it adopted a community-centred, participatory methodology. Journalists from two rural media organisations were brought together to exchange experiences grounded in their local contexts. Participants were introduced to AI tools for creative practice and critically exposed to the ways in which AI training data can be exclusionary or biased. This need was further underscored by a Thomson Reuters Foundation survey indicating that 57.6% of journalists are self-taught in AI, highlighting a significant gap in structured AI training (Radcliffe 2025)."),
                    ("p", "When even urban journalists in the Global Majority lack access to meaningful AI training, the idea that such knowledge will organically trickle down to rural newsrooms is an illusion. The roundtable's engagement with underrepresented populations was intentional in tackling this nonlinear knowledge diffusion of AI technology."),
                    ("p", "We structured the roundtable into the following key activities:"),
                    ("ul", [
                        "**Story Sharing and Reflection Sessions:** The participants shared their experiences of caste, gender and class-based racism and how covert racism reflects in their professional lives.",
                        "**Digging Deeper, Huddles, and Blue-Sky Speculations on AI Futures:** These deep-dives allowed participants to explore how racism manifests in AI systems and what kind of strategies are needed to design more inclusive, context-aware AI tools.",
                        "**Hands-on Practices with the Model Image and Video Trainer Tools:** The AI platform had created a Model Image Trainer Tool as well as a Video Generation tool. To create more equitable access to tech and to solve the language barrier, an AI agent was created which participants could use to speak in Hindi and generate prompts for the tools in English. Using the AI tools, participants trained their model trainer in their unique, aesthetic styles, thus experimenting with narrative generation and image and video creation. The digital interventions confronted UX challenges for non-English speakers and instilled confidence in them about AI.",
                    ]),
                    ("fig", 2, "Figure 2: Participants noting down their thoughts during a group exercise"),
                    ("ul", [
                        "**Peer Learning and Support:** We devised the roundtable in a way that participants could form cross-sector networks and connect beyond the project as well. This was meant to sustain collaboration and community-driven AI development. The roundtable imagined participants as co-creators of shared AI tools.",
                        "**An AI Curriculum for Journalists:** In order to bridge the data divide between AI users and rural communities with no access to AI, we used methods like reverse ideations and core huddles to create an AI curriculum for journalists from marginalised communities.",
                    ]),
                    ("h3", "Polyphonic AI"),
                    ("p", "These practices can be understood through the lens of polyphony and dialogism, as conceptualised by Mikhail Bakhtin. A polyphonic AI system includes multiple models, voices and perspectives rather than a single, overarching system. We designed several different tools for this roundtable, each uniquely tailored to participant needs. We used image trainers, video generation model trainers and an AI agent to help participants speak in Hindi and generate prompts for the image trainer. This AI agent was specially designed for the linguistic needs of the participants and Hindi-speaking cohort."),
                    ("p", "Our tools fostered interaction rather than a single, controlled mechanism and were dialogic and conversational. Thus, one could tailor their approach to AI systems in a polyphonic way. Applying Bakhtin's idea of polyphony and dialogism to AI can result in more democratic AI. Our Image trainer tools, for example, were first trained on participant datasets, thus creating a unique AI model for each participant. Then, this model was used to further generate datasets. We also allowed for zero data retention, thus upholding privacy and safety of participants."),
                    ("p", "The tools developed for the roundtable can be understood as anti-silencing interventions. The idea was to distribute control, authorship and participation across the cohort rather than reliance on a single, centralised system. Unlike conventional AI models that operate through centralised systems and employ dominant datasets, these tools were shaped through ongoing interaction with the participants, allowing them to actively influence both inputs and outputs. This shift from control to engagement enabled more plural and inclusive ways to interact with AI systems, thus ensuring that participant fears around AI could also be assuaged."),
                    ("p", "By facilitating multiple points of engagement, the tools disrupted the idea of a single authoritative system. Participants were able to generate and train their own image models using personalised datasets, resulting in multiple, unique outputs rather than a homogenised representation of what their culture looks like. This approach fostered a collaborative ecosystem of knowledge production."),
                    ("p", "Such a model supports greater diversity in representation, as it allows for a range of perspectives, aesthetics, and narratives to emerge simultaneously. In doing so, it challenges the silencing effects of dominant AI systems by big tech and opens up space for more equitable and context-sensitive forms of engagement."),
                    ("h3", "Participant Experiences"),
                    ("p", "Several participants highlighted the importance of creating safe learning environments for AI like the Shaping AI roundtable, which was a critical step towards a more inclusive, anti-racist AI designed in participatory ways. Participants saw value in further expanding the roundtable into a fellowship that would include more rural participants and journalists, and include scaffolded learning methods to ease their pathway towards creating and using AI tools."),
                    ("q", "We could make AI better by providing a space to learn safely while still protecting personal art and its equivalent. It shifts power as creators and communities get to decide how to share and protect their culture and stories.", "Participant"),
                    ("p", "Others drew attention to the representation gap within AI ecosystems, particularly for organizations like Chambal Media working at the intersections of gender, caste, and class."),
                    ("q", "As an organization which works with marginalized communities, and understands gender, caste, class in a much deeper way, we feel a huge gap when it comes to AI. The targeted audiences are also very different. What we need in this technology space is to make it more inclusive and to have more representation.", "Participant"),
                ],
            },
            {
                "num": "4",
                "id": "recommendations",
                "title": "Recommendations from the Roundtable",
                "blocks": [
                    ("p", "The imbalance within AI is not incidental but a structural flaw from bias in training data and non-inclusive systems and infrastructures design. As Dr. Katelyn Jones observes: 95 percent of images used to train AI models depict white skin, while medical algorithms often draw on U.S. military datasets in which women may constitute only six percent of subjects (Jones and Mattea 2020). The recommendations from this roundtable are conceptual and grounded in practice and lived experience."),
                    ("p", "The AI Now Institute notes, “claims of objectivity and neutrality in AI systems often mask underlying power relations and systemic biases embedded in the data and the institutions that produce it” (West, Whittaker, and Crawford 2019). This shocking statistic highlights what we have known all this while: data merely masquerades as objective while being riddled with biases. The centrality of community and creative participation thus becomes paramount and this roundtable was a small but important step towards that process. From the learnings at the roundtable, we gleaned the following recommendations:"),
                    ("ul", [
                        "**Establishing a Safe Context for AI Training for Journalists from Rural Communities:** It is imperative to create safe and financially supported spaces for women and other journalists from marginalised communities to experiment with AI and express themselves creatively. Our roundtable provided a space to a cohort of journalists to create images and videos in their creative styles, centering their everyday experiences and cultural contexts.",
                    ]),
                    ("fig", 3, "Figure 3: Cultural and context-aware outputs from the AI model image trainer — a contemporary Mughal-miniature style depiction of women on a motorbike and a journalistic avatar"),
                    ("ul", [
                        "**Anti-Racist AI Practices:** The roundtable delved deep into the question of what constitutes an anti-racist AI. Can an AI which is shaped by the biases of contemporary society be changed and made anti-racist by formulating legal frameworks? Or do we need different kinds of AI systems, which are the “utopian” versions of present AI from big tech? How can underrepresented voices be empowered in AI participation so that present-day AI is trained better and we also work towards an inclusive, sustainable AI for good? As Dancy and Saucier contend, focusing merely on bias in AI is insufficient and we must move towards examining the “design, development and deployment of AI systems” and cultures (Dancy and Saucier 2021). An anti-racist AI would reflect linguistic and cultural diversity and prevent cultural misappropriation. During the roundtable, participants observed how they could find stereotypes about their region, and gender in AI generated news content.",
                        "**Capacity Building Exercises for Digital Confidence:** The hands-on exercises with the AI tools demonstrated that participants could build AI confidence even without prior knowledge of AI. For this, we need tools which are tailored for different contexts. By creating an AI agent for Image Prompting, the AI platform helped non-English speakers use the tools with ease.",
                        "**Mitigating Biases in AI Systems through AI Literacy:** The roundtable showed that learning AI enabled storytelling allowed participants to engage more closely with algorithmic biases and relate them with their lived experiences. This turned their focus towards developing mitigating strategies like an AI curriculum for their peers and brainstorming on ethical frameworks for AI. Participants also viewed AI through a feminist lens, noting how it has stereotypes about what Indian women should look like. An AI generated image of an Indian woman had long dark hair, was clad in a kurta set and wore a bindi. Participants who were dressed differently from this AI representation and in varied ways understood the importance of creating AI images rooted in their personal and cultural narratives.",
                        "**Tool Iterations and Ethical Frameworks for an Inclusive AI:** The Model Image Trainer is designed in a way that it can be iterated with participant feedback. Following the roundtable, participant feedback was incorporated into subsequent iterations of the image trainer tool; turning it into an AI agent deployed on WhatsApp. The roundtable also brought fresh perspectives on ethical frameworks for safe and practical engagement with AI, like ensuring data privacy, attribution, and culturally sensitive use of AI outputs.",
                        "**Context Specific, Dialogic AI systems:** To respond to linguistic, social and cultural realities, it is necessary to design multimodal, dialogic AI systems which are context-specific. Participants in our roundtable were able to operate as interactive partners and design their own AI image trainers, which generated unique datasets in their own styles.",
                    ]),
                ],
            },
            {
                "num": "5",
                "id": "concluding-remarks",
                "title": "Concluding Remarks",
                "blocks": [
                    ("p", "The Shaping AI roundtable unearthed how AI surfaces racist stereotypes and linked it to everyday realities of gender and caste-based discrimination. It demonstrated how inclusive AI design needs to be intentional and participatory. While big tech firms use training data for fine-tuning their AI models, they do not collaborate with marginalized communities to truly erase biases or minimize them. This gap opens up the possibilities for open-source models which can be developed to be more culturally sensitive and nuanced through greater collaboration and transparency."),
                    ("p", "The roundtable highlighted how listening as a critical practice can counter the algorithmic silencing being done by AI systems to underrepresented communities. By incorporating lived experiences, multiple situated knowledge and aesthetic forms of expressions (image/video datasets), the roundtable foregrounded reciprocity, participation and collaboration. It was structured as a site for collective listening, where participants could share personal recollections and stories. As compared to an extractive model of AI development, a listening and practice-based approach lends itself to a more inclusive AI."),
                    ("p", "“Designing for ethical and inclusive AI refers to the intentional incorporation of human worth, autonomy, and identity into the fabric of AI systems” (Jain 2025). This roundtable showed that with intent, organisations can create spaces for pilot projects and training for AI, center lived experiences and reflect diverse cultural perspectives in AI."),
                    ("p", "Algorithmic bias is often treated as a technical issue of data composition; however, it may also be understood as a sociocultural phenomenon shaped by historically embedded structural inequalities. To fight bias and racism in AI systems, multi-perspective, polyphonic voices must be brought into the fold of these systems. Drawing from Bakhtin's idea of polyphony, in the context of AI “these principles emphasise the multiplicity of perspectives and the dynamic, dialogic interplay of various subjective consciousnesses, reflecting the inherent diversity of human thought.” (Karimova 2024)"),
                    ("p", "Critics may argue that an AI agent may not truly listen. But, it has been observed that single-point AI agents and systems too, tailor their answers based on prompts. The idea is to expand the training data to be representative of diverse voices – to truly build a “dialogue partner” rather than an “oracle of plausible responses”. (Schulbaum 2025)"),
                    ("p", "This approach suggests that AI is not simply neutral but can function as a space for multiple, coexisting voices. The use of multiple, context-specific tools, such as the image and video trainers developed for this roundtable, reflects a more decentralised approach to AI systems. When scaled, such approaches have the potential to support greater plurality and more democratic forms of engagement with AI."),
                    ("p", "To commit to an AI that is inclusive, anti-racist and equitable for all, organisations and policymakers need long-term community engagement. So that one day, a girl from a marginalized community in rural Uttar Pradesh can create an AI news anchor in her likeness rather than a white one, to report stories from her region, in her voice."),
                ],
            },
            {
                "id": "acknowledgements",
                "title": "Acknowledgements",
                "cls": "tight",
                "blocks": [
                    ("p", "The authors would like to thank Dev Aggarwal, Co-founder and CTO at Gooey.AI, for his invaluable technical guidance throughout this project. We are also grateful to Computational Mama, Head of Developer Relations at Gooey.AI, for her technical expertise and contributions. Finally, we sincerely acknowledge our project partners, the Goethe-Institut and the German Federal Agency for Civic Education (bpb), whose collaboration and support made this research possible."),
                ],
            },
            {
                "id": "ai-disclaimer",
                "title": "Disclaimer on the Use of AI",
                "cls": "tight",
                "blocks": [
                    ("p", "AI was used in the data collection for the roundtable. Participants created image and video datasets using AI tools. AI was also used for helping in formatting the paper, and language check. The paper is an original submission, free from ethical and plagiarism issues."),
                ],
            },
            {
                "id": "references",
                "title": "References",
                "cls": "ruled refs",
                "blocks": [
                    ("ul", [
                        "Chen, You, Ellen Wright Clayton, Laurie Lovett Novak, Shilo Anders, and Bradley Malin. 2023. “Human-Centered Design to Address Biases in Artificial Intelligence.” *Journal of Medical Internet Research* 25.",
                        "Costanza-Chock, Sasha. 2018. “Design Justice, A.I., and Escape from the Matrix of Domination.” *Journal of Design and Science*, no. 3. MIT Press. [jods.mitpress.mit.edu](https://jods.mitpress.mit.edu/pub/costanza-chock/release/4)",
                        "Dancy, Christopher L., and P. Khalil Saucier. 2021. “AI and Blackness: Toward Moving Beyond Bias and Representation.” *IEEE Transactions on Technology and Society*, 1–1. [doi.org/10.1109/TTS.2021.3125998](https://doi.org/10.1109/TTS.2021.3125998)",
                        "Hofmann, Valentin, Pratyusha Ria Kalluri, Dan Jurafsky, et al. 2024. “AI Generates Covertly Racist Decisions about People Based on Their Dialects.” *Nature* 633: 147–154. [doi.org/10.1038/s41586-024-07856-5](https://doi.org/10.1038/s41586-024-07856-5)",
                        "Karimova, Aygul. 2024. “Polyphony in AI: Towards Dialogic and Multiperspectival Systems.” *International Journal of Human–Computer Interaction*. [doi.org/10.1080/10447318.2024.2338661](https://doi.org/10.1080/10447318.2024.2338661)",
                        "Jain, Anushree. 2025. “Designing for Ethical and Inclusive AI through a Human-Centered Design Lens.” *Global Business & Economics Journal*, June 5, 2025. [gbej.org](https://gbej.org/articles/designing-for-ethical-and-inclusive-ai-through-a-human-centered-design-lens/)",
                        "Jones, Katelyn, and Nicole Mattea. 2020. “We Need a Feminist Approach to AI Development.” *Women in International Security (WIIS Global)*, June 5, 2020. [wiisglobal.org](https://wiisglobal.org/we-need-a-feminist-approach-to-ai-development/)",
                        "Platoniq. 2025. “Oracle or Dialogue Partner? Towards a Polyphonic AI Dialogue.” *Wilder Journal*. [journal.platoniq.net](https://journal.platoniq.net/en/wilder-journal-2/deep-dives/AI-dialogue/)",
                        "Radcliffe, Damian. 2025. *Journalism in the AI Era: Opportunities and Challenges in the Global South and Emerging Economies.* Thomson Reuters Foundation Insights Report. [trust.org](https://www.trust.org/wp-content/uploads/2025/01/TRF-Insights-Journalism-in-the-AI-Era.pdf)",
                        "Schiffrin, Anya. n.d. “AI and the Future of Journalism: An Issue Brief for Stakeholders.” In *World Trends in Freedom of Expression and Media Development*. UNESCO.",
                        "West, Sarah Myers, Meredith Whittaker, and Kate Crawford. 2019. *Discriminating Systems: Gender, Race, and Power in AI.* AI Now Institute. [ainowinstitute.org](https://ainowinstitute.org/publications/discriminating-systems-gender-race-and-power-in-ai-2)",
                    ]),
                ],
            },
        ],
    },

    # --------------------------------------------------------------- ICML 2026
    {
        "slug": "beyond-bias-evaluating-cultural-ai-through-participation-and-interpretation",
        "listed_as": "Beyond Bias: Evaluating Cultural AI Through Participation and Interpretation",
        "title": "Beyond Bias: Evaluating Cultural AI Through Participation and Interpretation",
        "status": "Preprint",
        "authors": AUTHORS_RCA,
        "abstract": (
            "Generative AI systems are increasingly understood as cultural technologies "
            "that produce and circulate meaning, yet their evaluation remains largely "
            "focused on harm mitigation through bias, fairness, and safety frameworks "
            "(Bender et al., 2021; Buolamwini & Gebru, 2018). This paper presents "
            "Beyond Bias, a collaboration between Gooey.AI and Goethe-Institut India, "
            "as a participatory framework for evaluating cultural AI combining "
            "collaborative dataset creation, artist-led model fine-tuning, accessible "
            "tooling, and co-authored governance practices. Drawing from participatory "
            "design and interpretive approaches, we propose three ideas for evaluating "
            "cultural AI systems: cultural integrity, participation and agency, and "
            "interpretive capacity, while also examining tensions around authorship, "
            "ownership, and cultural extraction in generative systems."
        ),
        "meta": [
            ("Venue", ["Culture × AI Workshop, ICML 2026, Seoul, South Korea"]),
        ],
        "sections": [
            {
                "num": "1",
                "id": "introduction",
                "title": "Introduction",
                "blocks": [
                    ("p", "Generative AI systems increasingly participate in the production of culture. Image, language, and video models generate artefacts that shape aesthetic norms, social narratives, and modes of expression across everyday life. As these systems become integrated into creative and cultural practices, they must be understood not only as computational tools but also as cultural technologies (Crawford, 2021). Current approaches to evaluating generative AI systems have primarily focused on harm mitigation. Existing research has addressed issues such as bias, misinformation, toxicity, fairness, and alignment with human values (Bender et al., 2021; Buolamwini & Gebru, 2018). These approaches remain essential, particularly given the structural inequalities embedded within large-scale datasets and machine learning pipelines. However, they also imply a limited definition of success: systems are considered culturally successful when they avoid producing harmful outcomes. This framing leaves underdeveloped a broader question: what does it mean for an AI system to engage culture well?"),
                    ("p", "The limitations of existing approaches become especially visible in culturally situated contexts. Generative models frequently reproduce dominant Western visual and linguistic norms while flattening local traditions, minority aesthetics, and contextual forms of knowledge into generic representations (Birhane, 2021; Crawford, 2021). Cultural nuance is often reduced to stylistic markers detached from lived practices, histories, and communities."),
                    ("p", "This paper presents Beyond Bias, a collaborative initiative between Gooey.AI and Goethe-Institut India that explores participatory approaches to cultural AI. Rather than treating culture as an external layer of evaluation, the project embeds cultural considerations directly within dataset creation, model training, interface design, and governance processes. Through collaborative workshops, artist-led fine-tuning, and co-authored manifestos, the initiative examines how AI systems might support culturally grounded forms of expression while preserving community agency and interpretive context."),
                    ("p", "The paper makes three contributions:"),
                    ("ul", [
                        "A participatory methodology for developing culturally situated generative AI systems through collaborative dataset creation and accessible tooling.",
                        "An interpretive framing of AI systems that positions generative models as technologies involved in meaning-making rather than neutral systems of pattern reproduction (Hall, 1997).",
                        "A framework for evaluating cultural AI systems based on cultural integrity, participation and agency, and interpretive capacity.",
                    ]),
                    ("p", "Ultimately, this work suggests that evaluating cultural AI requires looking beyond frameworks focused only on reducing harm, toward approaches that also consider cultural context, stewardship, interpretation, and what meaningful cultural outcomes might look like."),
                    ("h3", "1.1 From Bias Mitigation to Cultural AI"),
                    ("p", "Research on fairness and bias in AI has demonstrated how machine learning systems reproduce historical and structural inequalities embedded within training data (Buolamwini & Gebru, 2018). Studies of generative AI systems have highlighted disparities across race, gender, geography, and language. For instance, image models have been shown to perform less accurately on darker skin tones, and they often default to Western cultural norms and English-language contexts. These concerns have led to the development of mitigation strategies such as dataset balancing, filtering systems, fairness constraints, and model alignment techniques. While these approaches address important harms, they are often focused more on avoiding mistakes than on supporting meaningful cultural participation. In many cases, “cultural inclusion” is treated simply as having diverse representation in datasets, without considering how culture is interpreted, understood in context, or shaped by the communities involved."),
                    ("p", "Recent scholarship has increasingly framed generative AI as a cultural technology rather than merely an informational or computational system (Crawford, 2021). From this perspective, generative models do more than just repeat patterns from training data. They actively shape culture by creating images, stories, language, and visual styles that influence how people understand the world. For example, AI image generators can shape popular ideas of beauty, fashion, religion, or regional identity through the kinds of images they produce and circulate online. Their outputs resemble cultural artefacts traditionally studied within the humanities, requiring interpretive rather than purely statistical forms of evaluation (Hall, 1997)."),
                    ("p", "This shift raises important questions about how AI systems should be evaluated. If AI increasingly helps interpret and shape culture, then evaluation cannot depend only on numerical benchmarks or accuracy scores. Cultural meaning depends on context, history, and lived experience. For example, an AI-generated image of a religious ritual may appear visually accurate but still misrepresent its cultural meaning or significance. Evaluating cultural performance therefore requires attention to interpretation, aesthetics, provenance, and community experience."),
                    ("p", "Participatory and human-centered approaches to AI development offer one possible response to these limitations. Participatory design traditions emphasize co-creation, contextual expertise, and stakeholder involvement within technical systems (Sanders & Stappers, 2008). However, such methods have often remained peripheral within mainstream generative AI development, where datasets are typically extracted at scale with limited transparency or community governance (Couldry & Mejias, 2019). Beyond Bias builds upon participatory design approaches by integrating collaborative cultural practices directly into dataset curation, model fine-tuning, and governance structures for generative AI systems."),
                    ("h3", "1.2 Beyond Bias: A Participatory Framework for Cultural AI"),
                    ("p", "Beyond Bias is a collaborative initiative between Gooey.AI and Goethe-Institut India launched in March 2025 that explores participatory approaches to generative AI across cultural contexts. The project brought together artists, researchers, designers, and technologists from India, Germany, the United Kingdom, and the United States through workshops, roundtables, and collaborative experimentation. It featured over 200+ workshop participants and 24 member organisations in the stakeholders consortium."),
                    ("fig", 1, "Figure 1: Participants at the Beyond Bias Promptathon in Pune, India"),
                    ("p", "A central objective of the initiative was to examine how communities might participate more directly in shaping the datasets, tools, and governance structures underlying generative AI systems. The initiative was structured around three interconnected components:"),
                    ("ul", [
                        "**Manifesto and Collective Governance:** The initiative began by creating a consortia of institutional stakeholders across US, UK, EU and India. Over two roundtables they collaboratively authored an open manifesto articulating principles for culturally grounded AI development for model makers. Themes included cultural integrity, transparency, environmental accountability, fair compensation, and community stewardship. The manifesto functioned not only as an ethical framework and instigation for technical development of AI tools for cultural practitioners but also as a governance experiment that foregrounded collective authorship and participatory decision-making within AI development processes.",
                        "**Participatory Dataset Creation:** One core component of the project involved the collaborative creation of culturally situated datasets. Participants contributed image collections reflecting specific artistic traditions, visual languages, and regional aesthetics frequently underrepresented within dominant generative AI models. Rather than treating datasets as neutral repositories, the project approached dataset construction as a curatorial and interpretive practice. Decisions about what to include, how to categorize materials, and how to provide context became an important part of the cultural design process. Participants created innovative images and videos that featured variations on Mughal miniature styles, Japanese print styles, German folk art and Lascaux cave paintings, or among unique aesthetic styles from their own practices. Datasets, ethically sourced, were used to fine-tune generative image models and train LoRAs on these styles. A total of 1640 runs over 9 workshops created image and video outputs that better reflected specific cultural aesthetics, visual traditions, and contextual references.",
                    ]),
                    ("fig", 2, "Figure 2: AI Image Trainer Tool"),
                    ("ul", [
                        "**Accessible Tooling and Model Fine-Tuning:** The initiative also developed an AI Image Trainer tool and Video Generation Tool that enabled participants without extensive technical expertise to fine-tune generative models using curated datasets. To support under-resourced and marginalised creators working in different languages, we also developed a prompting tool that translated prompts from local languages like Hindi into English so they could be used with our existing visual tools. The tool lowered barriers to experimentation by simplifying model training workflows while also providing transparency regarding computational and environmental costs.",
                        "This approach redistributed aspects of technical agency toward artists and cultural practitioners typically excluded from model development processes and made them co-creators. Participants could actively shape how models interpreted visual forms rather than functioning solely as end-users of closed systems. Importantly, the project treated fine-tuning not just as a technical process, but as a way of negotiating between datasets, AI models, interfaces, and cultural context. Participants felt that the fine-tuned outputs reflected cultural details and visual aesthetics more accurately than the outputs generated by standard AI models by big tech.",
                    ]),
                    ("fig", 3, "Figure 3: Output Generated from the Beyond Bias Tool"),
                    ("p", "Together, these practices positioned Beyond Bias as both a technical and cultural intervention into how generative AI systems are designed, evaluated, and governed."),
                ],
            },
            {
                "num": "2",
                "id": "evaluating-cultural-ai",
                "title": "Evaluating Cultural AI",
                "blocks": [
                    ("p", "Existing evaluation frameworks for generative AI systems primarily focus on accuracy, alignment, safety, and fairness. While these metrics remain necessary, they are insufficient for assessing systems that increasingly participate in cultural production. A model may avoid explicit bias while still flattening cultural specificity, reproducing dominant aesthetics, or excluding communities from participation in system design. Similarly, representational diversity alone does not guarantee contextual understanding or meaningful cultural engagement. Based on insights from Beyond Bias, we propose three dimensions for evaluating cultural AI systems:"),
                    ("ul", [
                        "**Cultural Integrity:** Cultural AI systems should preserve and support the specificity of cultural forms rather than collapsing them into generalized or aestheticized representations. This includes attention to provenance, contextual meaning, historical relationships, and community knowledge. Cultural integrity requires more than simply adding visual styles or symbols from a culture into AI systems. The systems also need to understand the context and meaning behind them. For example, an AI model may be able to generate clothing that looks like a traditional sari, but still fail to capture its regional history, social meaning, or the cultural practices connected to how it is worn.",
                        "**Participation and Agency:** Communities should have meaningful influence over how datasets are created, how models are trained, and how outputs are deployed. Participation must extend beyond representation within datasets to include AI literacy, governance, authorship, and decision-making power. This dimension emphasizes AI development as a collaborative process rather than a purely extractive one.",
                        "**Interpretive Capacity:** Generative AI systems increasingly shape how cultural meaning is interpreted, rather than simply repeating patterns from data. Evaluation should therefore consider whether these systems can support context-aware interpretations informed by curated datasets, human input, and cultural expertise. This approach recognises that cultural meaning is shaped through relationships, history, and context, and cannot be fully measured through statistical performance alone.",
                    ]),
                    ("fig", 4, "Figure 4: Participants working with the AI Image Trainer"),
                    ("p", "Together, these dimensions propose a broader evaluative framework for cultural AI that incorporates qualitative, humanistic, and participatory criteria alongside technical performance."),
                    ("h3", "2.1 Tensions and Limitations"),
                    ("p", "While participatory approaches to cultural AI offer new possibilities for representation and agency, they also introduce significant tensions. Questions of authorship and ownership remain unresolved when models are trained on collaboratively curated cultural datasets. The generation of synthetic outputs derived from community knowledge raises concerns regarding consent, attribution, and intellectual property (Benjamin, 1935/2008). Participants frequently noted that mainstream image-generation systems reproduced Indian aesthetics through generalized visual stereotypes rather than regionally specific motifs and material traditions. Similarly, systems designed to preserve cultural forms may also enable new forms of extraction, replication, and appropriation (Couldry & Mejias, 2019). Cultural participation within AI development does not automatically eliminate structural inequalities surrounding access, labor, or institutional power."),
                    ("p", "The project also raises larger questions about how generative AI may change creative industries and cultural work. While easier fine-tuning tools can help more artists and communities participate, they may also change how creative work is produced, shared, and valued. For example, independent artists may gain new ways to create culturally specific designs, but companies could also use AI-generated versions of these styles without properly crediting or compensating the original communities. These challenges show that participatory cultural AI cannot be addressed through technical solutions alone. Ongoing governance and community oversight are also needed. As a result, evaluation frameworks should look not only at representation and model performance, but also at questions of power, labor, ownership, and accountability."),
                ],
            },
            {
                "num": "3",
                "id": "conclusion",
                "title": "Conclusion",
                "blocks": [
                    ("p", "As generative AI systems become increasingly embedded within cultural production, evaluating these systems requires moving beyond frameworks centered exclusively on harm mitigation. This paper presented Beyond Bias as a participatory and interpretive approach to cultural AI that integrates community engagement, collaborative dataset creation, accessible tools, and collective governance into AI system design. Rather than adding culture as an afterthought, the project integrates cultural values into the design, development, and organizational processes from the beginning."),
                    ("p", "We proposed three dimensions for evaluating cultural AI systems — cultural integrity, participation and agency, and interpretive capacity — as a framework for assessing positive cultural outcomes alongside questions of fairness and safety."),
                    ("p", "Cultural AI that is also inclusive requires attention to interpretation, cultural context, stewardship, and how communities create and share meaning. For example, an AI system may generate visually accurate traditional clothing, but still fail to represent the cultural history or social meaning connected to it. Future work should continue building participatory methods and governance structures that involve communities more directly in how AI systems are designed, trained, and evaluated. This can help create AI systems that are more context-aware, responsible, and accountable to the people and cultures they represent."),
                ],
            },
            {
                "id": "impact-statement",
                "title": "Impact Statement",
                "cls": "tight",
                "blocks": [
                    ("p", "This work contributes to ongoing discussions around the cultural, social, and ethical implications of generative AI systems. By proposing participatory and interpretive approaches to cultural AI, the paper explores how communities, artists, and cultural practitioners might play a more active role in shaping datasets, model development, and governance processes. The framework aims to support more culturally situated and context-sensitive AI systems while encouraging greater transparency and agency in AI development."),
                    ("p", "At the same time, this work recognizes that generative AI systems introduce significant risks, including cultural appropriation, extraction of community knowledge, unclear ownership of generated outputs, and potential impacts on creative labor. Participatory approaches alone do not eliminate structural inequalities in access, representation, or institutional power."),
                    ("p", "We therefore emphasize the importance of continued governance, accountability, and critical engagement when developing cultural AI systems iteratively. Participatory AI frameworks can balance innovation with the protection of cultural knowledge, creative rights, and community stewardship. These findings are preliminary, and future work will focus on further developing the Beyond Bias initiative by collaborating with communities such as rural journalists and community librarians, equipping them with AI literacy and training to build a more grounded and inclusive participatory framework."),
                ],
            },
            {
                "id": "references",
                "title": "References",
                "cls": "ruled refs",
                "blocks": [
                    ("ul", [
                        "Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency*, 610–623. [dl.acm.org](https://dl.acm.org/doi/10.1145/3442188.3445922)",
                        "Benjamin, W. (2008). *The work of art in the age of mechanical reproduction* (J. A. Underwood, Trans.). Penguin Books. (Original work published 1935)",
                        "Birhane, A. (2021). Algorithmic colonization of Africa. *SCRIPTed*, 17(2), 389–409. [script-ed.org](https://script-ed.org/article/algorithmic-colonization-of-africa/)",
                        "Buolamwini, J., & Gebru, T. (2018). Gender shades: Intersectional accuracy disparities in commercial gender classification. *Proceedings of Machine Learning Research*, 81, 1–15. [proceedings.mlr.press](https://proceedings.mlr.press/v81/buolamwini18a.html)",
                        "Costanza-Chock, S. (2020). *Design justice: Community-led practices to build the worlds we need.* MIT Press. [doi.org/10.7551/mitpress/12255.001.0001](https://doi.org/10.7551/mitpress/12255.001.0001)",
                        "Couldry, N., & Mejias, U. A. (2019). *The costs of connection: How data is colonizing human life and appropriating it for capitalism.* Stanford University Press. [sup.org](https://www.sup.org/books/sociology/costs-connection/excerpts)",
                        "Crawford, K. (2021). *Atlas of AI: Power, politics, and the planetary costs of artificial intelligence.* Yale University Press. [yalebooks.yale.edu](https://yalebooks.yale.edu/book/9780300264630/atlas-of-ai/)",
                        "Hall, S. (1997). *Representation: Cultural representations and signifying practices.* Sage Publications.",
                        "Harrington, C., Erete, S., & Piper, A. M. (2019). Deconstructing community-based collaborative design: Towards more equitable participatory design engagements. *Proceedings of the ACM on Human-Computer Interaction*, 3(CSCW), 1–25. [dl.acm.org](https://dl.acm.org/doi/10.1145/3359318)",
                        "Sanders, E. B.-N., & Stappers, P. J. (2008). Co-creation and the new landscapes of design. *CoDesign*, 4(1), 5–18. [doi.org/10.1080/15710880701875068](https://doi.org/10.1080/15710880701875068)",
                    ]),
                ],
            },
        ],
    },

    # ------------------------------------------------- RICE Workshop / C&C 2026
    {
        "slug": "beyond-bias-participatory-and-reflective-approaches-to-cultural-ai",
        "listed_as": "Beyond Bias: Participatory & Reflective Approaches to Cultural AI",
        "title": "Beyond Bias: Participatory and Reflective Approaches to Cultural AI",
        "status": "Preprint",
        "authors": [
            ("Archana Prasad", "Royal College of Art, London, UK", "archana.prasad@network.rca.ac.uk"),
            ("Isha Singh", "Gooey.AI, Lucknow, India", "coordinator@dara.network"),
            ("Tom Simmons", "Royal College of Art, London, UK", "tom.simmons@rca.ac.uk"),
        ],
        "abstract": (
            "Generative AI systems increasingly shape cultural production, yet creative "
            "intentions, cultural meanings, and interpretive practices often can't be "
            "articulated through computational metrics alone. This paper presents Beyond "
            "Bias, a collaboration between Gooey.AI and Goethe-Institut India, as a "
            "participatory approach to cultural AI which includes collaborative dataset "
            "creation, reflective AI tooling, artist-led model fine-tuning, and "
            "co-authored governance practices. Across 9 workshops involving over 200 "
            "participants, artists and cultural practitioners engaged with AI systems "
            "through experimentation, iteration, and collaborative LoRA training. "
            "Participants used their AI-generated outputs and visualizations as "
            "reflective interfaces for exploring symbolism, memory, authorship, and "
            "cultural contexts. Comparing contemporary generative AI outputs with "
            "participant fine-tuned outputs helped participants reflect on cultural "
            "details missing in big tech AI systems."
        ),
        "meta": [
            ("Keywords", [
                "Cultural AI, Human-AI Co-Creation, Reflective Creative Practice, "
                "Participatory Design, Creative Agency, Interpretive AI, Creative "
                "Interaction, AI and Creativity, Community-Centered AI, Generative AI"
            ]),
            ("Reference", [
                "Archana Prasad, Isha Singh, and Tom Simmons. 2026. Beyond Bias: "
                "Participatory and Reflective Approaches to Cultural AI. In Proceedings "
                "of The First Reflection in Creative Experience (RiCE) Workshop (RiCE "
                "W1). ACM Creativity & Cognition 2026, London, UK."
            ]),
        ],
        "sections": [
            {
                "num": "1",
                "id": "introduction",
                "title": "Introduction",
                "blocks": [
                    ("p", "Generative AI systems increasingly participate in cultural production. Image, language, and video models shape aesthetic norms, social narratives, and forms of expression across everyday life. As these systems become embedded within creative practice, they must be understood not only as computational tools but also as cultural technologies that mediate representation and meaning-making [1,4]."),
                    ("p", "Current approaches to evaluating generative AI systems have primarily focused on harm mitigation, including bias, toxicity, and misinformation. While these approaches remain necessary, they imply a limited definition of cultural success: systems are considered successful when they avoid harmful outputs [2]. This framing leaves a broader question unanswered: what does it mean for AI systems to engage culture well?"),
                    ("p", "Generative models frequently reproduce dominant Western visual and linguistic norms while flattening regional aesthetics and contextual forms of knowledge into generalized representations [1,3]. Cultural forms are often reduced to stylistic markers detached from lived practices, histories, and symbolism or erased altogether [4]."),
                    ("p", "This paper presents Beyond Bias, a collaborative initiative between Gooey.AI and Goethe-Institut India launched in March 2025, exploring participatory approaches to cultural AI through collaborative dataset creation, reflective tooling, and artist-led fine-tuning."),
                    ("p", "This paper contributes reflective AI tooling approaches foregrounding transparency, stewardship, and community participation; findings from participatory workshops examining how generative AI visualizations mediate cultural representation and interpretive practice; and a framework for cultural AI grounded in cultural integrity, and reflective practice."),
                ],
            },
            {
                "num": "2",
                "id": "cultural-participatory-approaches",
                "title": "Cultural and Participatory Approaches",
                "blocks": [
                    ("p", "Research on fairness and bias in AI has demonstrated how machine learning systems reproduce inequalities embedded within datasets and computational infrastructures [2]. Generative systems have been shown to privilege dominant Western visual and linguistic norms while not engaging with under-represented communities. Image generation by big tech models often shows stereotyped outputs for certain communities. E.g. Indian women may be represented as clad in sarees, with bindis and luscious black hair."),
                    ("p", "Recent scholarships increasingly frame generative AI systems as cultural technologies rather than purely informational systems. Crawford describes AI infrastructures as deeply entangled with social, political, and material systems [1]. Critical scholars have also argued that contemporary AI infrastructures frequently reproduce extractive relationships between platforms, datasets, and communities [3,6]. These concerns become particularly important in cultural contexts where local knowledge, aesthetics, and histories may be absorbed into AI datasets without meaningful consent, attribution, or governance."),
                    ("p", "Participatory and human-centered approaches to AI development emphasize stakeholder involvement, situated expertise, and collaborative design [5]. Through Beyond Bias, we build upon participatory approaches by positioning artists and cultural practitioners not only as users of AI systems, but as co-creators and active participants in dataset creation, fine-tuning, interpretation, and governance."),
                ],
            },
            {
                "num": "3",
                "id": "beyond-bias-initiative",
                "title": "The Beyond Bias Initiative",
                "blocks": [
                    ("p", "Beyond Bias involved over 200 participants and 24 organizations across nine workshops involving collaborative dataset creation, prompt experimentation, LoRA training, and reflective discussion. We co-created an open manifesto with participants and used that as scaffolding to inform the development of AI tools."),
                    ("p", "The initiative began by creating a consortia of institutional stakeholders across US, UK, EU and India. Over two roundtables they collaboratively authored an open manifesto articulating principles for culturally grounded AI development for model makers. Themes included cultural integrity, transparency, environmental accountability, fair compensation, and community stewardship. The manifesto functioned not only as an ethical framework and instigation for technical development of AI tools for cultural practitioners but also as a governance experiment that foregrounded collective authorship and participatory decision-making within AI development processes. Each Beyond Bias workshop was an iteration on the previous one, and led to updates in our two major tools — the AI Image Trainer tool and the Video Generation tool."),
                    ("h3", "3.1 Reflective Tool Design"),
                    ("p", "A central component of the initiative involved the development of reflective AI tools designed not only for generation, but also for transparency, participation, and stewardship."),
                    ("p", "The project developed accessible image fine-tuning and video-generation tools that enabled participants without extensive tech expertise to train LoRAs using collaboratively curated datasets. Participants could experiment with multilingual prompting workflows, including Hindi-to-English prompt translation systems designed to support under-resourced languages. Images were trained using Flux, and participants could choose from multiple models to generate their outputs, thus supporting creative agency and intent."),
                    ("fig", 1, "Figure 1: AI Image Trainer Tool with ecological costs displayed at the bottom"),
                    ("p", "The tools also incorporated low-resolution generation options and lightweight pathways that foregrounded environmental awareness. Tools shared the eco cost of each run, in terms of water and electricity usage. This reflected broader concerns around the material and ecological costs of AI infrastructures [1]. Discussions surrounding privacy, consent, and cultural extraction informed the sessions as well. Our recent Beyond Bias workshop at the Royal College of Art, conducted in collaboration with the Mozilla Foundation, enabled participants to choose whether their generated datasets could be shared publicly and contribute to the training of future AI models."),
                    ("p", "Rather than positioning participants solely as end-users of AI systems, the project explored how localized fine-tuning and participatory tooling could create pathways for communities to influence broader generative ecosystems."),
                    ("h3", "3.2 Participatory Workshops and Cultural Outputs"),
                    ("p", "Participants frequently observed that LLMs produced flattened and generalized representations of culturally specific aesthetics. Prompts referencing Mughal miniatures, regional folk art, or embroidery traditions often generated outputs that appeared visually ornate while overlooking compositional structure, symbolism, material texture, and regional variation."),
                    ("p", "For example, prompts related to Mughal miniature traditions frequently resulted in generic “Indian royal court” imagery characterized by symmetrical palace settings, decorative clothing, and homogenized visual motifs. Participants noted that these outputs lacked the narrative density, and layered symbolism associated with miniature traditions. Outputs associated with “Indian art” often emphasized saturated colors, exoticized ornamentation, or spiritual symbolism. Similarly, prompts related to embroidery and folk-art practices often turned distinct regional aesthetics into generalized craft imagery. One participant generated image and video outputs based on her embroidery practice, allowing local histories and material traditions to inform the AI-generated outputs."),
                    ("fig", 2, "Figure 2: Participants during the Beyond Bias Promptathon in New Delhi, October 2025"),
                    ("p", "Participants also created variants of the Lascaux Cave Paintings, a style intentionally introduced to examine how generative AI systems engage with forms of cultural heritage that fall outside dominant contemporary or commercially visible aesthetic categories. While baseline AI systems often generated generic prehistoric cave scenes, participants were able to create outputs that better reflected the textures, animal forms, and visual style of the original paintings."),
                    ("q", "The conversation wasn't only on developing or improving AI models but on questions of bias and representation embedded within the dataset itself.", "Workshop participant"),
                    ("p", "This highlighted how workshops became spaces for critical reflection on the cultural assumptions shaping generative AI systems. These interactions prompted broader discussions concerning how generative systems encode dominant cultural assumptions and flatten contextual forms of knowledge [3,4]."),
                    ("p", "Participants generated alternative outputs reflecting more situated cultural interpretations like reinterpretations of Mughal miniature traditions depicting women protesting in New Delhi, riding bicycles, and engaging contemporary political contexts."),
                    ("fig", 3, "Figure 3: Women riding a bike — output in Mughal miniature style"),
                    ("p", "Across workshops, participants conducted more than 1,600 generation runs involving iterative experimentation with prompts, datasets, and fine-tuned models. Workshops functioned as iterative cycles of co-design in which participant feedback directly informed subsequent tooling decisions, dataset practices, and governance discussions [5]. Participants increasingly described the tools not simply as systems for image generation, but as creative scaffolds for reflecting on authorship, representation, and cultural interpretation itself."),
                    ("fig", 4, "Figure 4: Metrics from the Beyond Bias workshop in Pune, with 242 runs"),
                ],
            },
            {
                "num": "4",
                "id": "framework",
                "title": "A Framework for Cultural AI",
                "blocks": [
                    ("p", "Beyond Bias emphasized the importance of contextual understanding, interpretive agency, and community stewardship within generative systems. Based on workshop reflections, participatory tooling practices, and collaborative experimentation, we propose four interconnected dimensions for cultural AI:"),
                    ("ul", [
                        "**Cultural Integrity:** Cultural AI systems should preserve contextual meaning, symbolism, provenance, and historical relationships embedded within cultural forms rather than reducing culture to surface-level visual aesthetics [4]. Participants repeatedly emphasized that generated outputs may appear stylistically accurate while still failing to represent the social, political, and historical meanings associated with cultural practices.",
                        "**Participation and Agency:** Participants emphasized that communities should be able to shape AI systems directly through dataset curation, fine-tuning, prompting workflows, and governance discussions. Participatory approaches therefore position cultural practitioners not only as users of AI systems, but as co-creators of generative infrastructures [5].",
                        "**Interpretive Capacity:** Participants frequently used generated outputs as prompts for reflection and reinterpretation rather than as final creative artefacts. Workshops became spaces where participants critically examined how prompts, datasets, and interfaces shaped representation itself. Cultural AI systems therefore require the capacity to support dialogue and critical engagement rather than simply automating cultural reproduction [4].",
                        "**Stewardship and Governance:** Participants also foregrounded concerns surrounding ownership, consent, environmental impact, and cultural extraction within generative AI systems [1,6].",
                    ]),
                ],
            },
            {
                "num": "5",
                "id": "conclusion",
                "title": "Conclusion",
                "blocks": [
                    ("p", "Participatory approaches to cultural AI create new possibilities for representation and creative agency while also introducing tensions concerning ownership, labor, consent, and scalability. A participant described the initiative as “wielding a machete through the jungle of AI bias with fellow explorers,” emphasizing the experimental, collaborative, and uncertain nature of navigating AI systems."),
                    ("p", "Although collaborative fine-tuning enabled more culturally situated outputs, participants frequently reflected on the limitations of working within commercial foundation-model ecosystems trained on opaque datasets [1,6]."),
                    ("p", "Beyond Bias suggests that participatory cultural AI requires moving beyond harm mitigation toward systems that support cultural integrity, interpretive agency, and community stewardship. Rather than treating culture as extractable data, cultural AI frameworks that foreground reflection may enable communities to become active co-creators of AI."),
                ],
            },
            {
                "id": "acknowledgments",
                "title": "Acknowledgments",
                "cls": "tight",
                "blocks": [
                    ("p", "We thank Dev Aggarwal, CTO of Gooey.AI and Computational Mama (Head of Developer Relations) for their technical guidance and support throughout the Beyond Bias initiative. We also gratefully acknowledge Goethe-Institut / Max Mueller Bhavan New Delhi for its partnership and collaboration in enabling the Beyond Bias workshops and participatory research that informed this work."),
                ],
            },
            {
                "id": "references",
                "title": "References",
                "cls": "ruled refs",
                "blocks": [
                    ("ul", [
                        "Kate Crawford. 2021. *Atlas of AI: Power, Politics, and the Planetary Costs of Artificial Intelligence.* Yale University Press.",
                        "Emily M. Bender, Timnit Gebru, Angelina McMillan-Major, and Shmargaret Shmitchell. 2021. On the dangers of stochastic parrots: Can language models be too big? In *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency*. 610–623.",
                        "Abeba Birhane. 2021. Algorithmic colonization of Africa. *SCRIPTed* 17, 2 (2020), 389–409.",
                        "Stuart Hall. 1997. *Representation: Cultural Representations and Signifying Practices.* Sage Publications.",
                        "Elizabeth B.-N. Sanders and Pieter Jan Stappers. 2008. Co-creation and the new landscapes of design. *CoDesign* 4, 1 (2008), 5–18.",
                        "Nick Couldry and Ulises A. Mejias. 2019. *The Costs of Connection: How Data Is Colonizing Human Life and Appropriating It for Capitalism.* Stanford University Press.",
                    ]),
                ],
            },
        ],
    },
]
