import sys
import os

sys.path.insert(0,(os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))))

from paralogia import dictionary




def test_word_search():
	results = dictionary.get_translations_en_ja('dog')
	assert results['en_ja_results']['animal'] == '犬 | 狗'

	results = dictionary.get_translations_ja_en('犬')
	assert results[0] == ' いぬ (犬) : 1. dog (Canis (lupus) familiaris) '

def test_sentence_search():
	results = dictionary.get_example_sentences('犬')
	assert results['The dog came running to us.'] == 'その犬は私たちのほうへ走ってきました。'
