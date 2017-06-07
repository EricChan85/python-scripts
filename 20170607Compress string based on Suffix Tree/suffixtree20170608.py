import string

POSITIVE_INFINITY = 1 << 30

class Node:
    def __init__(self, suffix_link=None):
        self.suffix_link = suffix_link

    def __repr__(self):
        return 'Node(' + str(self.suffix_link) + ')'

class Edge:
    def __init__(self, src_node_idx, dst_node_idx, first_char_idx, last_char_idx):
        self.src_node_idx = src_node_idx
        self.dst_node_idx = dst_node_idx
        self.first_char_idx = first_char_idx
        self.last_char_idx = last_char_idx

    def split(self, suffix, suffix_tree):
        return split_edge(self, suffix, suffix_tree)

    def __len__(self):
        return self.last_char_idx - self.first_char_idx + 1

    def __repr__(self):
        return 'Edge(' + str(self.src_node_idx) + ', ' +\
        str(self.dst_node_idx) + ', ' + \
        str(self.first_char_idx) + ', ' + \
        str(self.last_char_idx) + ')'


def split_edge(edge, suffix, suffix_tree):
    #alloc new node
    new_node = Node()#suffix.src_node_idx
    suffix_tree.nodes.append(new_node)
    new_node_idx = len(suffix_tree.nodes) - 1
    #alloc new edge
    new_edge = Edge(new_node_idx, edge.dst_node_idx, edge.first_char_idx + len(suffix), edge.last_char_idx)
    suffix_tree.insert_edge(new_edge)
    #shorten existing edge
    edge.last_char_idx = edge.first_char_idx + len(suffix) - 1
    edge.dst_node_idx = new_node_idx
    return new_node_idx

        
class Suffix:
    def __init__(self, src_node_idx, first_char_idx, last_char_idx):
        self.src_node_idx = src_node_idx
        self.first_char_idx = first_char_idx
        self.last_char_idx = last_char_idx

    def is_explicit(self):
        return is_explicit_suffix(self)

    def is_implicit(self):
        return is_implicit_suffix(self)

    def canonize(self, suffix_tree):
        canonize_suffix(self, suffix_tree)

    def __repr__(self):
        return 'Suffix(' + str(self.src_node_idx) + ', ' + str(self.first_char_idx) + ', ' + str(self.last_char_idx) + ')'

    def __len__(self):
        return self.last_char_idx - self.first_char_idx + 1

def is_explicit_suffix(suffix):
    return suffix.first_char_idx > suffix.last_char_idx

def is_implicit_suffix(suffix):
    return not is_explicit_suffix(suffix)

def canonize_suffix(suffix, suffix_tree):
    if not suffix.is_explicit():
        edge = suffix_tree.edge_lookup[suffix.src_node_idx, suffix_tree.string[suffix.first_char_idx]]
        if(len(edge) <= len(suffix)):
            suffix.first_char_idx += len(edge)
            suffix.src_node_idx = edge.dst_node_idx
            canonize_suffix(suffix, suffix_tree)
        

class SuffixTree:
    def __init__(self, string, alphabet=None):
        self.string = string
        self.string_length = len(string)
        if alphabet == None:
            alphabet = set(string)
        self.alphabet = alphabet
        self.nodes = [Node()]
        self.edge_lookup = {} #edge_source_node_first_char_dict
        self.active_point = Suffix(0, 0, -1)
        for i in range(len(string)):
            add_prefix(i, self.active_point, self)

    def insert_edge(self, edge):
        self.edge_lookup[edge.src_node_idx, self.string[edge.first_char_idx]] = edge

    def remove_edge(self, edge):
        del self.edge_lookup[edge.src_node_idx, self.string[edge.first_char_idx]]
        

def add_prefix(last_char_idx, active_point, suffix_tree):
    last_parent_node_idx = -1
    while True:
        parent_node_idx = active_point.src_node_idx
        if active_point.is_explicit():
            if (active_point.src_node_idx, suffix_tree.string[last_char_idx]) in suffix_tree.edge_lookup: #already in tree
                break
        else:
            edge = suffix_tree.edge_lookup[active_point.src_node_idx, suffix_tree.string[active_point.first_char_idx]]
            if suffix_tree.string[edge.first_char_idx + len(active_point)] == suffix_tree.string[last_char_idx]: #the given prefix is already in the tree, do nothing
                break
            else:
                parent_node_idx = edge.split(active_point, suffix_tree)
        suffix_tree.nodes.append(Node(-1))
        new_edge = Edge(parent_node_idx, len(suffix_tree.nodes) - 1, last_char_idx, POSITIVE_INFINITY)##################
        suffix_tree.insert_edge(new_edge)
        #add suffix link
        if last_parent_node_idx > 0:
            suffix_tree.nodes[last_parent_node_idx].suffix_link = parent_node_idx
        last_parent_node_idx = parent_node_idx
        if active_point.src_node_idx == 0:
            active_point.first_char_idx += 1
        else:
            active_point.src_node_idx = suffix_tree.nodes[active_point.src_node_idx].suffix_link
        active_point.canonize(suffix_tree)
    if last_parent_node_idx > 0:
        suffix_tree.nodes[last_parent_node_idx].suffix_link = parent_node_idx
    #last_parent_node_idx = parent_node_idx
    active_point.last_char_idx += 1
    active_point.canonize(suffix_tree)

#validation code
import collections
is_valid_suffix = collections.defaultdict(lambda: False)
branch_count = collections.defaultdict(lambda: 0)
def is_valid_suffix_tree(suffix_tree):
    walk_tree(suffix_tree, 0, {}, 0)
    for i in range(1, len(suffix_tree.string)):
        if not is_valid_suffix[i]:
            print ('not is_valid_suffix[%s]' % str(i))
            #return False
    leaf_sum = 0
    branch_sum = 0
    for i in range(len(suffix_tree.nodes)):
        if branch_count[i] == 0:
            print ('logic error')
            return False
        elif branch_count[i] == -1:
            leaf_sum += 1
        else:
            branch_sum += branch_count[i]
    if leaf_sum != len(suffix_tree.string):
        print ('leaf_sum != len(suffix_tree.string)')
        print ('leaf_sum:', leaf_sum)
        return False
    if branch_sum != len(suffix_tree.nodes) - 1: #root dosn't have edge leading to it
        print ('branch_sum != len(suffix_tree.nodes) - 1')
        return False
    return True

def walk_tree(suffix_tree, current_node_idx, current_suffix, current_suffix_len):
    edges = 0
    for c in suffix_tree.alphabet:
        try:
            edge = suffix_tree.edge_lookup[current_node_idx, c]
            if current_node_idx != edge.src_node_idx:
                raise Exception('eeeeeeeeeeeeeeeeee!!!!!!!!!!!')
            #print (current_node_idx, edge.src_node_idx)
            if branch_count[edge.src_node_idx] < 0:
                print ('error: node labeled as leaf has children!')
            #print (branch_count[edge.src_node_idx])
            branch_count[edge.src_node_idx] += 1
            edges += 1
            l = current_suffix_len
            for j in range(edge.first_char_idx, edge.last_char_idx + 1):
                current_suffix[l] = suffix_tree.string[j]
                l += 1
            if walk_tree(suffix_tree, edge.dst_node_idx, current_suffix, l):
                if branch_count[edge.dst_node_idx] > 0:
                    print ('error: leaf labeled as having children')
                branch_count[edge.dst_node_idx] -= 1 #leaves have '-1' children
        except KeyError:
            pass
    if edges == 0:
        #leaf. check suffix
        is_valid_suffix[current_suffix_len] = ''.join(current_suffix[i] for i in range(current_suffix_len)) == suffix_tree.string[-(current_suffix_len):]
        print (''.join(current_suffix[i] for i in range(current_suffix_len)))
        if not is_valid_suffix[current_suffix_len]:
            print ('not is_valid_suffix[current_suffix_len]')
        ###########################################################
        return True
    else:
        return False

class RepeatedSubstr:
    def __init__(self, sub_str, repeat_times, start_idx):
        self.repeat_substr = sub_str
        self.repeat_times = repeat_times
        self.repeat_start_idx = start_idx

    def __key(self):
        return (self.repeat_substr, self.repeat_start_idx, self.repeat_times)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash(self):
        return hash(selft.__key())

    def get_sub_str_length(self):
        return len(self.repeat_substr) * self.repeat_times
        

def walk_tree(suffix_tree, current_node_idx, current_suffix, current_suffix_len):
    edges = 0
    for c in suffix_tree.alphabet:
        try:
            edge = suffix_tree.edge_lookup[current_node_idx, c]
            if current_node_idx != edge.src_node_idx:
                raise Exception('eeeeeeeeeeeeeeeeee!!!!!!!!!!!')
            #print (current_node_idx, edge.src_node_idx)
            if branch_count[edge.src_node_idx] < 0:
                print ('error: node labeled as leaf has children!')
            #print (branch_count[edge.src_node_idx])
            branch_count[edge.src_node_idx] += 1
            edges += 1
            l = current_suffix_len
            for j in range(edge.first_char_idx, edge.last_char_idx + 1):
                current_suffix[l] = suffix_tree.string[j]
                l += 1
            if walk_tree(suffix_tree, edge.dst_node_idx, current_suffix, l):
                if branch_count[edge.dst_node_idx] > 0:
                    print ('error: leaf labeled as having children')
                branch_count[edge.dst_node_idx] -= 1 #leaves have '-1' children
        except KeyError:
            pass
    if edges == 0:
        #leaf. check suffix
        is_valid_suffix[current_suffix_len] = ''.join(current_suffix[i] for i in range(current_suffix_len)) == suffix_tree.string[-(current_suffix_len):]
        print (''.join(current_suffix[i] for i in range(current_suffix_len)))
        if not is_valid_suffix[current_suffix_len]:
            print ('not is_valid_suffix[current_suffix_len]')
        ###########################################################
        return True
    else:
        return False

def get_suffix_str(suffix_tree, current_node_idx, current_suffix, current_suffix_len, suffix_str_list):
    edges = 0
    for c in suffix_tree.alphabet:
        try:
            edge = suffix_tree.edge_lookup[current_node_idx, c]
            edges += 1
            l = current_suffix_len
            for j in range(edge.first_char_idx, edge.last_char_idx + 1):
                current_suffix[l] = suffix_tree.string[j]
                l += 1
            get_suffix_str(suffix_tree, edge.dst_node_idx, current_suffix, l, suffix_str_list)
        except KeyError:
            pass
    if edges == 0:        
        suffix_str_list.append(''.join(current_suffix[i] for i in range(current_suffix_len)))

def deal_single_str(sub_str, string_length, result_list):
    sub_str_length = len(sub_str)
    r_length = 1
    i = 0
    while i + 2 * r_length < sub_str_length:
        repeat_sub_str = sub_str[i:i + r_length]
        if repeat_sub_str == sub_str[i + r_length:i + 2 * r_length]:
            print (repeat_sub_str, 2, string_length - sub_str_length + i)
            result_list.append(RepeatedSubstr(repeat_sub_str, 2, string_length - sub_str_length + i))
            break #i += r_length
        else:
            r_length += 1            
            

def get_repeat_sub_str(suffix_str_list, string_length, result_list):
    for sub_str in suffix_str_list:
        deal_single_str(sub_str, string_length, result_list)
        
def show_edge(suffix_tree, src_node_idx, first_char):
    edge = suffix_tree.edge_lookup[src_node_idx, first_char]
    print (edge)
    print (suffix_tree.string[edge.first_char_idx:edge.last_char_idx+1])

def show_node(node_idx):
    for c in ALPHABET:
        try:
            edge = suffix_tree.edge_lookup[node_idx, c]
            print (edge)
            print (suffix_tree.string[edge.first_char_idx:edge.last_char_idx+1])
        except KeyError:
            pass
    print (str(node_idx) + ' -> ' + str(suffix_tree.nodes[node_idx]))
    

#bbbababba
#abaaabab
test_str = 'babababbaaaaababbbab$'#'mississippi$'
print (test_str)
POSITIVE_INFINITY = len(test_str) - 1
suffix_tree = SuffixTree(test_str)
#is_valid = is_valid_suffix_tree(suffix_tree)
#print ('is_valid_suffix_tree:', is_valid)
suffix_str_list = []
get_suffix_str(suffix_tree, 0, {}, 0, suffix_str_list)
print (suffix_str_list)
sub_str_list = []
get_repeat_sub_str(suffix_str_list, suffix_tree.string_length, sub_str_list)

import operator
sub_str_list.sort(key=operator.attrgetter("repeat_start_idx"), reverse=True)
print ("----del-share-----")
has_share_char = True
while has_share_char:
    if len(sub_str_list) == 1:
        has_share_char = False
        break
    for i in range(len(sub_str_list) - 1):
        if sub_str_list[i].repeat_start_idx < sub_str_list[i+1].repeat_start_idx + sub_str_list[i+1].get_sub_str_length() and sub_str_list[i].repeat_substr != sub_str_list[i+1].repeat_substr:
            del sub_str_list[i+1]
            has_share_char = True
            break
        else:
            has_share_char = False        

print ("-----connect-same---------")
filtered_sub_str_list = []
for i in range(len(sub_str_list)):
    for j in range(i + 1, len(sub_str_list)):
        #share character  aaa=>(a)3
        if sub_str_list[i].repeat_substr == sub_str_list[j].repeat_substr and sub_str_list[i].repeat_start_idx == (sub_str_list[j].repeat_start_idx + sub_str_list[j].get_sub_str_length() - len(sub_str_list[i].repeat_substr)):
            sub_str_list[j].repeat_times += (sub_str_list[i].repeat_times - 1)
            filtered_sub_str_list.append(sub_str_list[i])
            break
        #continus  aaaa=>(a)4
        if sub_str_list[i].repeat_start_idx == (sub_str_list[j].repeat_start_idx + sub_str_list[j].get_sub_str_length()) and sub_str_list[i].repeat_substr == sub_str_list[j].repeat_substr:
            sub_str_list[j].repeat_times += sub_str_list[i].repeat_times
            filtered_sub_str_list.append(sub_str_list[i])
            break
sub_str_list = [item for item in sub_str_list if item not in filtered_sub_str_list]
print ("----")
for r_s in sub_str_list:
    print (r_s.repeat_substr, r_s.repeat_start_idx, r_s.repeat_start_idx + r_s.get_sub_str_length() - 1, r_s.get_sub_str_length(), r_s.repeat_times)

for r_s in sub_str_list:
    test_str = test_str[:r_s.repeat_start_idx] + "(" + r_s.repeat_substr + ")" + str(r_s.repeat_times) + test_str[r_s.repeat_start_idx + r_s.get_sub_str_length():]
print (test_str)
