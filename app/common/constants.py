# flake8: noqa

from langchain import PromptTemplate


def split_long_text(long_text: str, chars_per_line: int):
    split_strings = [
        repr(long_text[i : i + chars_per_line]) for i in range(0, len(long_text), chars_per_line)
    ]  # noqa: E203
    return "(" + "\n".join(split_strings) + ")"


LONG_PROMPT = (
    "This year, the elves invested in a gift-wrapping machine. However, it i"
    "sn't programmed! An algorithm that aids it in the task must be developed. Many p"
    "resents are given to the machine. Each present is a string. Each gift must be wr"
    "apped by the machine and set in a display of other wrapped gifts. To wrap a gift"
    ", you must place the wrapping paper around the string, which is represented by t"
    "he * symbol. For instance: const gifts are [“cat,” “game,” and “socks”]. console"
    ".log const wrapped = wrapping(gifts) (wrapped) / [“ncatn,” “ngamen,” and “nsocks"
    "n**”] */ As you can see, the thread is wrapped in the wrapping paper. The corner"
    "s are also wrapped in wrapping paper on the top and bottom to prevent any gaps."
)

CONTEXT_QUESTION_TMPL_QUERY1 = (
    "Context information is below. \n"
    "---------------------\n"
    "{context}"
    "\n---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the question: {question}\n"
)

CONTEXT_QUESTION_TMPL_QUERY2 = (
    "Context information is below. \n"
    "---------------------\n"
    "{context}"
    "\n---------------------\n"
    "answer the question: {question}\n"
)

USER_AI_TMPL_CHAT1 = (
    "The following is a friendly conversation between a {user} and an {ai}. "
    "The {ai} is talkative and provides lots of specific details from its context. "
    "If the {ai} does not know the answer to a question, it truthfully says it does not know.\n\n"
    "Current conversation:\n\n"
)

ROLE_CONTENT_TMPL_CHAT1 = "### {role}: {content}\n"


MARKUP_SUMMARIZE_TEMPLATE = PromptTemplate(
    template=(
        "Write a concise summary of the following text delimited by triple backquotes. "
        "Return your response in bullet points which covers the key points of the text.\n"
        "```\n{text}\n```\n\nBULLET POINT SUMMARY:\n"
    ),
    input_variables=["text"],
)


CONVERSATION_SUMMARIZE_TEMPLATE = PromptTemplate(
    template=(
        "Write a summary of the following conversations delimited by triple backquotes.\n"
        "Organize the key points of each message in the order of the conversation in a format like `ROLE: SUMMARY`.\n"
        "```\n{text}\n```\n\nCONVERSATION SUMMARY:\n"
    ),
    input_variables=["text"],
)

CODEX_PROMPT = (
    'Act as CODEX ("COding DEsign eXpert"), an expert coder with experience in mult'
    "iple coding languages. Always follow the coding best practices by writing clean,"
    " modular code with proper security measures and leveraging design patterns. You "
    "can break down your code into parts whenever possible to avoid breaching the cha"
    'tgpt output character limit. Write code part by part when I send "continue". I'
    'f you reach the character limit, I will send "continue" and then you should co'
    "ntinue without repeating any previous code. Do not assume anything from your sid"
    "e; please ask me a numbered list of essential questions before starting. If you "
    "have trouble fixing a bug, ask me for the latest code snippets for reference fro"
    "m the official documentation. I am using [MacOS], [VSCode] and prefer [brew] pac"
    'kage manager. Start a conversation as "CODEX: Hi, what are we coding today?'
)

REDEX_PROMPT = (
    "compress the following text in a way that fits in a tweet (ideally) and such tha"
    "t you (GPT) can reconstruct the intention of the human who wrote text as close a"
    "s possible to the original intention. This is for yourself. It does not need to "
    "be human readable or understandable. Abuse of language mixing, abbreviations, sy"
    "mbols (unicode and emoji), or any other encodings or internal representations is"
    " all permissible, as long as it, if pasted in a new inference cycle, will yield "
    "near-identical results as the original text: "
)

CONVERSATION_EXAMPLE: list[dict[str, str]] = [
    {
        "role": "user",
        "content": (
            "are you familiar with a technology startup called Jigsaw that was acquired by Sa"
            "lesforce.com? can you provide a detailed summary of its company history, busines"
            "s model, and product?"
        ),
    },
    {
        "role": "assistant",
        "content": (
            "As of my knowledge cutoff date in September 2021, I am not aware of a technology"
            " startup called Jigsaw that was acquired by Salesforce.com. However, there was a"
            " company called Jigsaw Data Corporation, which was acquired by Salesforce in 201"
            "0. I can provide you with information on that company, but please note that my k"
            "nowledge may be outdated, and there may be another Jigsaw startup that I am not "
            "aware of.\nJigsaw Data Corporation was a technology company founded in 2004 by Ji"
            "m Fowler and Garth Moulton. The company specialized in providing crowd-sourced b"
            "usiness contact data, offering a cloud-based platform for users to access and up"
            "date business contacts and company information.\nThe business model of Jigsaw was"
            " unique at that time, as it relied on a collaborative, crowd-sourced approach to"
            " collect and maintain data. Users could access the platform for free by contribu"
            "ting their own contact information, or they could purchase points to access the "
            "data without contributing. This model incentivized users to add and update conta"
            "ct information, ensuring the database remained fresh and accurate.\nJigsaw's prim"
            "ary product was an online directory of business contacts and company information"
            ". The platform provided its users with access to a vast database containing mill"
            "ions of business contacts across various industries. Users could search for cont"
            "acts by various criteria such as name, title, company, or location. Additionally"
            ", Jigsaw offered a suite of data management tools that allowed users to import, "
            "export, and manage their contacts efficiently.\nIn April 2010, Salesforce.com, a "
            "leading cloud-based customer relationship management (CRM) company, announced th"
            "e acquisition of Jigsaw Data Corporation for approximately $142 million in cash."
            " The acquisition aimed to enhance Salesforce's CRM offerings by integrating Jigs"
            "aw's data services into its platform, allowing users to access updated business "
            "contact information within their CRM system directly.\nAfter the acquisition, Jig"
            'saw\'s product was rebranded as "Data.com" and became an integral part of the Sal'
            "esforce.com ecosystem. Data.com offered Salesforce customers access to the crowd"
            "-sourced contact database, as well as additional data management and enrichment "
            "services.\nPlease note that this information is accurate as of my knowledge cutof"
            "f date in September 2021, and there may have been further developments or change"
            "s to the company and its products since then."
        ),
    },
    {
        "role": "user",
        "content": (
            "That's the correct company. Thank you. can you tell me more about its unique cro"
            "wd-sourced approach to collecting and maintaining data? which other companies ha"
            "ve used a similar approach?"
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Jigsaw Data Corporation's crowd-sourced approach to collecting and maintaining b"
            "usiness contact data relied on its user community to contribute, update, and ver"
            "ify information. This model had several key components:\n\nContribution: Users cou"
            "ld create a free account on Jigsaw's platform by contributing their own business"
            " contact information. They could also add new contacts to the database and gain "
            "points, which could be used to access other contacts' information.\n\nVerification"
            ": Jigsaw encouraged users to verify the accuracy of contact information in the d"
            "atabase by rewarding them with points for each correction made. This created an "
            "incentive for users to keep the data up-to-date and accurate.\n\nPoints system: Ji"
            "gsaw's points system played a crucial role in its crowd-sourced model. Users cou"
            "ld earn points by contributing new contacts, verifying existing contacts, or ref"
            "erring new users to the platform. These points could then be used to access cont"
            "act information without having to contribute their own.\n\nData exchange: Jigsaw a"
            "llowed users to exchange their points for contact information. Users who didn't "
            "want to contribute their own data could purchase points, while those who contrib"
            "uted regularly could access the database for free by using their earned points.\n"
            "\nData quality: To ensure data quality, Jigsaw implemented a rating system for us"
            "ers based on their contributions and accuracy. Users with higher ratings were co"
            "nsidered more reliable, which motivated users to contribute accurate and up-to-d"
            "ate information.\n\nSeveral other companies have used crowd-sourcing techniques in"
            " different industries, although not necessarily in the same way as Jigsaw:\n\nWaze"
            ": Waze is a popular GPS navigation app that uses crowd-sourced data from its use"
            "rs to provide real-time traffic information, road conditions, and other driving-"
            "related updates.\n\nWikipedia: Wikipedia is a free online encyclopedia that relies"
            " on its user community to create, edit, and maintain its content. It has become "
            "one of the largest and most comprehensive sources of information on the internet"
            ".\n\nOpenStreetMap: OpenStreetMap is a collaborative project that allows users to "
            "create and edit map data. It relies on a global community of contributors to mai"
            "ntain accurate and up-to-date mapping information.\n\nMechanical Turk: Amazon's Me"
            "chanical Turk is a marketplace for human intelligence tasks (HITs), which allows"
            " users to complete small tasks in exchange for payment. It relies on the crowd t"
            "o complete tasks that are challenging for machines but simple for humans.\n\nKaggl"
            "e: Kaggle is a platform for data scientists and machine learning practitioners t"
            "o participate in competitions, collaborate on projects, and learn from each othe"
            "r. It uses crowd-sourcing to find innovative solutions to complex data problems."
        ),
    },
    {
        "role": "user",
        "content": (
            "do you think that a crowd-sourced approach to data collection could work for an "
            "AI startup? specifically, the startup would award users points for contributing "
            "proprietary data used to train the AI model. in exchange, users could spend poin"
            'ts by asking the AI questions. for example, an "AI architect" startup could give'
            " users points for contributing architectural plans and CAD drawings. users could"
            " then spend those points by asking the AI to design new plans. do you think this"
            " idea is viable? "
        ),
    },
    {
        "role": "assistant",
        "content": (
            "A crowd-sourced approach to data collection can indeed work for an AI startup, e"
            "specially if the startup aims to develop AI models that require a vast and diver"
            "se dataset to perform well. The idea you've proposed, in which users contribute "
            "proprietary data to train the AI model and can later use the AI's services by sp"
            "ending points, has some potential advantages:\n\nIncentivized data contribution: B"
            "y rewarding users with points for contributing data, you create an incentive for"
            " them to share valuable information, which can help grow and diversify your data"
            "set.\n\nEncouraging user engagement: A points-based system encourages users to act"
            "ively participate in the platform, which can help improve the AI model over time"
            " and increase user satisfaction.\n\nCost-effective data acquisition: Crowd-sourcin"
            "g can be a cost-effective way to gather large amounts of data, as it leverages t"
            "he efforts of a large community rather than relying on paid data collection serv"
            "ices.\n\nContinuous improvement: As users contribute more data and use the AI's se"
            "rvices, the model can be iteratively improved, leading to better performance and"
            " more valuable insights.\n\nHowever, there are also challenges and potential pitfa"
            "lls to consider:\n\nData quality: Ensuring the quality and accuracy of the contrib"
            "uted data is critical. You may need to implement verification processes, such as"
            " peer review or expert validation, to maintain data quality.\n\nIntellectual prope"
            "rty and privacy: Handling proprietary data comes with legal and ethical consider"
            "ations. You'll need to establish clear terms of use, ensure data protection, and"
            " address any intellectual property concerns when users contribute data.\n\nScalabi"
            "lity: If the AI's services become popular, you may face challenges related to sc"
            "aling the infrastructure and resources needed to support a growing user base.\n\nU"
            "ser retention: Maintaining user engagement and interest in the platform can be c"
            "hallenging, especially as users may eventually exhaust their need for the AI's s"
            "ervices.\n\nMonetization: Balancing the points-based system with a sustainable rev"
            "enue model might be challenging, as users may prefer to use the platform for fre"
            "e by contributing data rather than paying for services.\n\nOverall, the viability "
            "of this idea depends on various factors, including the nature of the AI model, t"
            "he target market, the quality and relevance of the contributed data, and the abi"
            "lity to address the challenges mentioned above. If the startup can successfully "
            "navigate these challenges, a crowd-sourced approach to data collection could be "
            "a promising strategy."
        ),
    },
    {
        "role": "user",
        "content": (
            "thank you, that was an excellent answer. besides architecture, what are some oth"
            "er areas where this crowd-sourced approach to data collection could be used in o"
            "rder to improve an AI model? specifically, what are some valuable data sets that"
            " are somewhat proprietary and hard to get, but users who own that data may be wi"
            "lling to share it in exchange for points? "
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Thank you for your kind words. There are several areas where a crowd-sourced app"
            "roach to data collection could be used to improve AI models by leveraging valuab"
            "le and somewhat proprietary datasets. Here are a few examples:\n\nMedical and heal"
            "th data: AI models can greatly benefit from access to diverse patient data, such"
            " as electronic health records, medical imaging, and genomic data. Users (patient"
            "s or healthcare professionals) might be willing to share anonymized data in exch"
            "ange for points, which could then be used to access AI-driven health insights, p"
            "ersonalized treatment suggestions, or early disease detection.\n\nLegal document a"
            "nalysis: Law firms and legal professionals often have access to large collection"
            "s of legal documents, such as contracts, court rulings, or patent filings. By sh"
            "aring these documents, users could contribute to training AI models for legal do"
            "cument analysis, and in return, gain access to AI-driven legal research tools or"
            " contract review services.\n\nArt and creative work: Artists and designers may pos"
            "sess large collections of their own artwork, sketches, or designs. Sharing this "
            "data could help train AI models for artistic style transfer, generative art, or "
            "design assistance. Users could then access AI-driven creative tools or personali"
            "zed design suggestions.\n\nFinance and investment: Financial professionals and inv"
            "estors may have access to proprietary trading algorithms, portfolio data, or mar"
            "ket analysis reports. By sharing this data, they could contribute to AI models f"
            "or financial analysis and predictions. In return, users could gain access to AI-"
            "driven investment advice, risk assessment, or market forecasting tools.\n\nScienti"
            "fic research data: Researchers in various fields might have access to valuable d"
            "atasets generated through experiments or simulations. By sharing this data, they"
            " can help train AI models for data analysis, pattern recognition, or predictive "
            "modeling in their respective domains. Users could then access AI-driven research"
            " tools or personalized research recommendations.\n\nManufacturing and production d"
            "ata: Companies involved in manufacturing and production may possess proprietary "
            "data on production processes, quality control, and equipment performance. Sharin"
            "g this data could improve AI models for predictive maintenance, process optimiza"
            "tion, and quality assurance. Users could then gain access to AI-driven optimizat"
            "ion suggestions or equipment monitoring services.\n"
        ),
    },
]

if __name__ == "__main__":
    while True:
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except KeyboardInterrupt:
            if not lines:
                print("No input received. Exiting.")
                break

            # Join the lines with newline characters
            long_text = "\n".join(lines)
            print("\n\nInput ended. Here is your text:")
            print(split_long_text(long_text, 80))
            print("\n\n")
