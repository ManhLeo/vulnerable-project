DictionaryValue* InitialLoadObserver::GetTimingInformation() const {
    ListValue* items = new ListValue;
    for (TabTimeMap::const_iterator it = loading_tabs_.begin();
         it != loading_tabs_.end();
         ++it) {
      DictionaryValue* item = new DictionaryValue;
      base::TimeDelta delta_start = it->second.start_time() - init_time_;
  
      item->SetDouble("load_start_ms", delta_start.InMillisecondsF());
      if (it->second.stop_time().is_null()) {
        item->Set("load_stop_ms", Value::CreateNullValue());
      } else {
        base::TimeDelta delta_stop = it->second.stop_time() - init_time_;
        item->SetDouble("load_stop_ms", delta_stop.InMillisecondsF());
      }
      items->Append(item);
    }
    DictionaryValue* return_value = new DictionaryValue;
    return_value->Set("tabs", items);
    return return_value;
  }