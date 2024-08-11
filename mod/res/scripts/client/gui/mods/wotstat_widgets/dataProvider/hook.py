def registerEvent(cls, method_name):
  def decorator(new_method):
    orig_method = getattr(cls, method_name, None)

    def wrapper(self, *args, **kwargs):
      if orig_method is not None:
        orig_result = orig_method(self, *args, **kwargs)
        
      try:
        new_method(self, *args, **kwargs)
      except Exception as e:
        print("An error occurred in the custom method: {}".format(e))
      
      return orig_result

    setattr(cls, method_name, wrapper)
    return new_method

  return decorator