class TrieNode :
    def __init__(self):
        self.children = {}
        self.isLeaf = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        length = len(word)
        for i in range(length):
            if i == length-2:
                continue
            ch = word[i]
            if ch in current.children:
                node = current.children[ch]
            else:
                node = TrieNode()
                current.children[ch] = node
            current = node
        current.isLeaf = True

    def searchTrie(self, word):
        current = self.root
        length = len(word)
        for i in range(length):
            ch = word[i]
            if current.children[ch] is None:
                return False
            print(ch)
            current = current.children[ch]
        return True

    def buildclasshierarchy(self):
        class_hierarchy = {}
        current = self.root
        self.dfs(class_hierarchy, current)
        return class_hierarchy

    def dfs(self, class_hierarchy, current):
        for childkey, relatednode in current.children.items():
            if relatednode.isLeaf:
                return
            class_hierarchy[childkey] = relatednode.children.keys()
            self.dfs(class_hierarchy, relatednode)

if __name__ == '__main__':
    word = ["VSOnline", "AgileInsights", "WIZ", 1]
    word2 = ["VSOnline", "Expert Team", "WIT IQ", 2]
    word3 = ["VSOnline", "UI Zone", "WIT PI", 3]
    trie = Trie()
    trie.insert(word)
    trie.insert(word2)
    trie.insert(word3)
    class_hierarchy = trie.buildclasshierarchy()
    for key, value in class_hierarchy.items():
        print(key, value)

