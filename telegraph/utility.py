

def break_up_text_box(text_box_str):

    text_box_list = text_box_str.split("\n")
    return_list = []

    for one_line in text_box_list:
        one_line=''.join(ch for ch in one_line if ch.isalnum())
        return_list.append(one_line.strip())

    return(return_list)