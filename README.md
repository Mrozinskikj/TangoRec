# TangoRec - Intelligent Vocabulary Recommendation for Japanese Language Learning
Sentence mining, a method where learners extract sentences with unfamiliar words from their reading material for later study, is highly effective but can disrupt the learning flow. This fragmentation can make language immersion feel like a chore, as learners must constantly pause to note down new words and sentences. TangoRec is designed to streamline this process. By offering bulk vocabulary learning recommendations based on immersion content and tailored to the learner's existing knowledge, TangoRec distinctly separates immersion from study. This approach allows for a smoother learning experience, where learners can either prepare for easier reading by familiarising themselves with key vocabulary beforehand, or consolidate their knowledge afterwards.

TangoRec constructs an approximate model of a learner's language knowledge by lemmatising their knowledge corpus, such as an Anki flashcard collection. Unknown words from the immersion content are identified, ranked by frequency, and presented alongside dictionary definitions and source sentences.

Tokenisation via Sudachi paired with UniDic enable TangoRec to accurately parse the learner's immersion content and make correct recommendations. This is particularly important for Japanese, which lacks word segmentation markers, and has complex grammatical inflections.

A full description of the software is given [here](http://kmroz.com/tangorec.html).

# Running the Software
The software has been compiled into a single executable file under exe/tangorec.exe. This may be launched without any further installation. It is recommended to place this file within an empty folder, as the software will create data files.

The source python code is located in source/main.py.

A lightweight version of the algorithm without a GUI exists in Python Notebook form as source/notebook.ipnyb.

Aside from knowledge and learning content files, the software requires word frequency data and a JMDict dictionary to function. Sample frequency data may be found [here](http://kmroz.com/tangorec/freq.txt), and dictionary file [here](https://github.com/FooSoft/yomichan/raw/dictionaries/jmdict_english.zip).

Code has been tested with Python 3.10.11.
