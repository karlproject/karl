
import deform

#import translationstring
#_ = translationstring.TranslationStringFactory('karl')


# --
# Define our custom widgets here
#
#
# If we just override a widget's template, no code is needed
# here, it is enough to place the modified template in our
# templates directory.
#
# However, in some cases we need a custom widget, and this
# is the example to make them::
#
#     class OtherTextInputWidget(deform.widget.TextInputWidget):
#         template = "othertextinput"
#         ...
#
# Then use this widget from the schema::
#
#    import forms
#
#    class Schema(colander.Schema):
#        firstname = colander.SchemaNode(colander.String(),
#                    widget=forms.widget.MyTextInputWidget(),\
#                       description=u'First Name')
#
#


class KarlRichTextWidget(deform.widget.RichTextWidget):
    template = 'karlrichtext'

