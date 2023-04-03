import re

{None: set(('uncategorized',1)), 'Ohio': {'Cleveland': set(('Cleveland', 1000)), 'Toledo': set(('Toledo',100))}}

class LocationForest:
    def __init__(self):
        self.structure = {None:set()}

    def add(self, item):
        self.structure[None].add(item)
    
    def __str__(self):
        return str(self.structure)

    def __repr__(self):
        return repr(self.structure)

    def __getitem__(self, labels):
        if labels is None:
            return self.structure[None]
        if not isinstance(labels, tuple):
            labels = (labels,)
        if len(labels)==1:
            try:
                return self.structure[labels[0]]
            except KeyError:
                self.structure[labels[0]] = set()
                return self.structure[labels[0]]
        try:
            return self.structure[labels[0]][labels[1:]]
        except KeyError:
            self.structure[labels[0]] = LocationForest()
            return self.structure[labels[0]][labels[1:]]

    def categorize(self, regex, label):
        uncategorized = set()
        while self.structure[None]:
            location = self.structure[None].pop()
            if regex.search(location[0]):
                self[label].add(location)
            else:
                uncategorized.add(location)
        self.structure[None] = uncategorized

    def select(self, regex):
        matched = set()
        for location in self.structure[None]:
            if regex.search(location[0]):
                matched.add(location)
        return matched

    def __len__(self):
        length = 0
        for key in self.structure.keys():
            length += len(self[key])
        return length

    def __iter__(self):
        return iter(self[None])

    def __contains__(self, item):
        contains = False
        for container in self.structure.values():
            if item in container:
                return True
        return False


    def uncategorize(self, label, item):
        try:
            self[label].remove(item)
            self[None].add(item)
        except KeyError:
            raise

    def head(self, labels=None, n=10):
        return sorted(self[labels],key=lambda x: -x[1])[:n]        

    def interactive_reject(self, labels=None):
        if isinstance(self[labels],LocationForest):
            labels += (None,)
        rejects = set()
        for item in sorted(self[labels],key=lambda x:-x[1]):
            response = input(f"{item}: ")
            if response == 'x':
                rejects.add(item)
        for reject in rejects:
            self.uncategorize(labels,reject)

def traverse(location_forest,keys=None):
    if isinstance(location_forest, set):
        for location in location_forest:
            yield (location[0], keys)
    else:
        for key, value in location_forest.structure.items():
            if keys is None and key is not None:
                next_keys = (key,)
            elif key is not None:
                next_keys = keys + (key,)
            elif keys is not None:
                next_keys = keys
            else:
                next_keys = tuple()
            for location in traverse(value, next_keys):
                yield location
