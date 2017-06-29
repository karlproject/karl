from repoze.folder.interfaces import IFolder

class IMetricsContainerFolder(IFolder):
    """ A marker interface for the folder that houses metrics"""

class IMetricsYearFolder(IFolder):
    """ A marker interface for the metrics year folder"""

class IMetricsMonthFolder(IFolder):
    """ A marker interface for the metrics month folder"""
