# ASN.1 types tags
from string import join

__all__ = [ 'TagSet' ]

tagClassUniversal = 0x00
tagClassApplication = 0x40
tagClassContext = 0x80
tagClassPrivate = 0xC0

tagFormatSimple = 0x00
tagFormatConstructed = 0x20

tagCategoryImplicit = 0x01
tagCategoryExplicit = 0x02
tagCategoryUntagged = 0x04

class TagSet:
    def __init__(self, tagClass, tagFormat, tagId, tagCategory):
        self.tagClass = ( tagClass, )
        self.tagFormat = ( tagFormat, )
        self.tagId = ( tagId, )
        self.tagCategory = ( tagCategory, )
        self.__taggingSequence = None
    
    def __repr__(self):
        return join(map(lambda a,b,c: str(a)+'|'+str(b)+'|'+str(c),
                    self.tagClass, self.tagFormat, self.tagId), ',')

    def clone(self, **kwargs):
        myClone = self.__class__(0,0,0,0)
        myClone.tagClass=self.tagClass
        myClone.tagFormat=self.tagFormat
        myClone.tagId=self.tagId
        myClone.tagCategory=self.tagCategory        
        if kwargs:
            myClone.tagClass=(kwargs.get('tagClass', self.tagClass[0]),) + \
                              myClone.tagClass
            myClone.tagFormat=(kwargs.get('tagFormat', self.tagFormat[0]),) + \
                               myClone.tagFormat
            myClone.tagId=(kwargs.get('tagId', self.tagId[0]),) + \
                           myClone.tagId
            myClone.tagCategory=(kwargs.get('tagCategory', self.tagCategory[0]),)+\
                                 myClone.tagCategory
        return myClone

    def __getitem__(self, idx):
        return self.tagClass[idx], self.tagFormat[idx], \
               self.tagId[idx], self.tagCategory[idx]

    def __cmp__(self, other):
        return cmp(
            (self.tagClass, self.tagFormat, self.tagId, self.tagCategory),
            (other.tagClass, other.tagFormat, other.tagId, other.tagCategory)
            )
    
    def __hash__(self):
        return hash(
            (self.tagClass, self.tagFormat, self.tagId, self.tagCategory)
            )
    
    def getTaggingSequence(self):
        if self.__taggingSequence is None:
            self.__taggingSequence = ()
            for tagClass, tagFormat, tagId, tagCategory in map(
                None, self.tagClass, self.tagFormat, self.tagId, self.tagCategory
                ):
                if tagCategory == tagCategoryUntagged:
                    break
                self.__taggingSequence = (
                    tagClass | tagFormat | tagId,
                    ) + self.__taggingSequence
                if tagCategory == tagCategoryImplicit:
                    break
        return self.__taggingSequence

if __name__ == '__main__':
    t = TagSet(1,2,3,2)
    t = t.clone(tagClass=9)
    print t
    for a in t:
        print a
    print t.getTaggingSequence()
