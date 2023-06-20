# TangoRec - Intelligent Vocabulary Recommendation for Japanese Language Learning
An effective method for language learning is immersion through text-based content, followed by studying new words extracted from these materials. However, recording unfamiliar words can disrupt the language learning flow and is time-intensive. TangoRec is a Python-based algorithmic tool designed to mitigate this issue by offering vocabulary recommendations based on the learner’s provided content and current language knowledge.

TangoRec constructs an approximate model of a learner's language knowledge through lemmatization of their knowledge corpus, such as an Anki flashcard collection. Unfamiliar lemmas from the learning content are identified, ranked by frequency, and presented alongside dictionary definitions, source sentences, and part-of-speech tags.

A full description of the software is given [here](http://kmroz.com/tangorec.html).

# Running the Software
The software has been compiled into a single executable file as tangorec.exe, forgoing the need for installation of any dependencies.

Alternatively, the software may be executed via the gui.py file.

A lightweight version of the algorithm without a GUI exists in Python Notebook form as notebook.ipnyb.

Aside from knowledge and learning content files, the software requires word frequency data and a JMDict dictionary to function. Sample frequency data may be found [here](http://corpus.leeds.ac.uk/frqc/internet-jp.num), and dictionary file [here](https://github.com/FooSoft/yomichan/raw/dictionaries/jmdict_english.zip).

Code has been tested with Python 3.10.11.
