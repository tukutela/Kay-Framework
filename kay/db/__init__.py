
from google.appengine.ext import db
from werkzeug.utils import import_string

from kay.conf import settings
from kay.utils import local
from kay.utils import forms
import simplejson

class OwnerProperty(db.ReferenceProperty):

  def __init__(self, **kwargs):
    if not 'reference_class' in kwargs:
      kwargs['reference_class'] = import_string(settings.AUTH_USER_MODEL)
    super(OwnerProperty, self).__init__(**kwargs) 

  def default_value(self):
    if hasattr(local, 'request') and hasattr(local.request, 'user'):
      if local.request.user.is_anonymous():
        return None
      else:
        return local.request.user.key()
    return None
        
class StringListPropertySeparatedWithComma(db.StringListProperty):
  def get_form_field(self, **kwargs):
    """Return a Django form field appropriate for a StringList property.

    This defaults to a Textarea widget with a blank initial value.
    """
    defaults = {'field': forms.TextField(), 'form_class': forms.CommaSeparated,
                'min_size': 0}
    defaults.update(kwargs)
    return super(StringListPropertySeparatedWithComma, self).\
        get_form_field(**defaults)

  def get_value_for_form(self, instance):
    """Extract the property value from the instance for use in a form.

    This joins a list of strings with newlines.
    """
    value = db.ListProperty.get_value_for_form(self, instance)
    if not value:
      return None
    if isinstance(value, list):
      value = ','.join(value)
    return value

  def make_value_from_form(self, value):
    """Convert a form value to a property value.

    This breaks the string into lines.
    """
    if not value:
      return []
    if isinstance(value, basestring):
      value = value.split(",")
    return value
  

class StringListPropertyPassThrough(db.StringListProperty):

  def get_value_for_form(self, instance):
    """Extract the property value from the instance for use in a form.

    This joins a list of strings with newlines.
    """
    value = db.ListProperty.get_value_for_form(self, instance)
    if not value:
      return None
    return value

  def make_value_from_form(self, value):
    """Convert a form value to a property value.

    This breaks the string into lines.
    """
    if not value:
      return []
    return value

class JsonProperty(db.TextProperty):
	def validate(self, value):
		return value 
	
	def get_value_for_datastore(self, model_instance):
		result = super(JsonProperty, self).get_value_for_datastore(model_instance)
		result = simplejson.dumps(result)
		return db.Text(result)
		
	def make_value_from_datastore(self, value):
		try:
			value = simplejson.loads(str(value))
		except:
			pass #do nothing if its not a JSON object
		return super(JsonProperty, self).make_value_from_datastore(value)