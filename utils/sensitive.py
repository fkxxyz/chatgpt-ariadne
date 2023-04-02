import ahocorasick

# 敏感词过滤模块
from rwlock import RWLock

from ordered_set import OrderedSet
from typing import Iterator

default_sensitive_word = '\u5171\u532A'


class SensitiveFilter:
    def __init__(self, w1: str, w2: str):
        """
        :param w1: 第一类敏感词文件路径
        :param w2: 第二类敏感词文件路径
        """
        self.__w1 = w1
        self.__w2 = w2

        self.__lock1 = RWLock()
        self.__lock2 = RWLock()

        self.__words_1 = OrderedSet()
        self.__words_2 = OrderedSet()

        self.automaton_1 = ahocorasick.Automaton()
        self.automaton_2 = ahocorasick.Automaton()

        self.reload()

    # 重新加载敏感词文件
    def reload(self):
        self.__words_1.clear()
        try:
            with open(self.__w1, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    self.__words_1.add(line.strip())
        except FileNotFoundError:
            pass
        self.__words_2.clear()
        try:
            with open(self.__w2, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    self.__words_2.add(line.strip())
        except FileNotFoundError:
            pass

        self.automaton_1 = ahocorasick.Automaton()
        for index, word in enumerate(self.__words_1.items):
            self.automaton_1.add_word(word, (index, word))
        else:
            self.__words_1.add(default_sensitive_word)
            self.automaton_1.add_word(default_sensitive_word, (0, default_sensitive_word))
        self.automaton_1.make_automaton()

        self.automaton_2 = ahocorasick.Automaton()
        for index, word in enumerate(self.__words_2.items):
            self.automaton_2.add_word(word, (index, word))
        else:
            self.__words_2.add(default_sensitive_word)
            self.automaton_2.add_word(default_sensitive_word, (0, default_sensitive_word))
        self.automaton_2.make_automaton()

    # 获取所有的第一类敏感词，返回可迭代对象
    def get_words_1(self) -> Iterator[str]:
        return self.__words_1.items

    # 获取所有的第二类敏感词，返回可迭代对象
    def get_words_2(self) -> Iterator[str]:
        return self.__words_2.items

    # 动态添加第一类敏感词，参数为敏感词数组，并去重保存到文件
    def add_words_1(self, words: Iterator[str]):
        try:
            self.__lock1.acquire()
            for word in words:
                self.automaton_1.add_word(word, (len(self.__words_1), word))
            self.automaton_1.make_automaton()

            # 去重
            self.__words_1.update(words)

            # 保存到文件
            with open(self.__w1, 'w', encoding='utf-8') as f:
                for word in self.__words_1:
                    f.write(word + '\n')
        finally:
            self.__lock1.release()

    # 动态添加第二类敏感词，参数为敏感词数组，并去重保存到文件
    def add_words_2(self, words: Iterator[str]):
        try:
            self.__lock2.acquire()
            for word in words:
                self.automaton_2.add_word(word, (len(self.__words_2), word))
            self.automaton_2.make_automaton()

            # 去重
            self.__words_2.update(words)

            # 保存到文件
            with open(self.__w2, 'w', encoding='utf-8') as f:
                for word in self.__words_2:
                    f.write(word + '\n')
        finally:
            self.__lock2.release()

    # 动态删除第一类敏感词，参数为敏感词数组，存到文件
    def remove_words_1(self, words: Iterator[str]):
        try:
            self.__lock1.acquire()
            for word in words:
                self.automaton_1.remove_word(word)
            self.automaton_1.make_automaton()

            # 去重
            self.__words_1.difference_update(words)

            # 保存到文件
            with open(self.__w1, 'w', encoding='utf-8') as f:
                for word in self.__words_1:
                    f.write(word + '\n')
        finally:
            self.__lock1.release()

    # 动态删除第二类敏感词，参数为敏感词数组，存到文件
    def remove_words_2(self, words: Iterator[str]):
        try:
            self.__lock2.acquire()
            for word in words:
                self.automaton_2.remove_word(word)
            self.automaton_2.make_automaton()

            # 去重
            self.__words_2.difference_update(words)

            # 保存到文件
            with open(self.__w2, 'w', encoding='utf-8') as f:
                for word in self.__words_2:
                    f.write(word + '\n')
        finally:
            self.__lock2.release()

    # 过滤一段文本的第一类敏感词，将敏感词替换为 *，返回是否存在敏感词和替换后的文本
    def filter_1(self, text: str) -> (bool, str):
        result = text
        replaced = False
        try:
            self.__lock1.acquire_read()
            for end_index, (insert_order, original_value) in self.automaton_1.iter(text):
                begin_index = end_index - len(original_value) + 1
                result = result[:begin_index] + '*' * len(original_value) + result[end_index + 1:]
                replaced = True
        finally:
            self.__lock1.release_read()
        return replaced, result

    # 判断一段文本是否存在第二类敏感词，返回是否存在敏感词
    def filter_2(self, text: str) -> bool:
        try:
            self.__lock2.acquire_read()
            for end_index, (insert_order, original_value) in self.automaton_2.iter(text):
                return True
        finally:
            self.__lock2.release_read()
        return False
