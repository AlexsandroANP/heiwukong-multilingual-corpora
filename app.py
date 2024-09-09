import streamlit as st
import json
import os



def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)



def extract_options_from_data(data):
    categories  = []
    attributes  = {}
    languages   = set()

    for category, attr_dict in data.items():
        categories.append(category)
        attributes[category] = []
        for attribute, id_dict in attr_dict.items():
            attributes[category].append(attribute)
            for lang_dict in id_dict.values():
                languages.update(lang_dict.keys())

    return categories, attributes, list(languages)



def filter_languages(lang_dict, languages):
    if languages is None:
        return lang_dict
    if all(lang in lang_dict for lang in languages):
        return {lang: lang_dict[lang] for lang in languages}
    return None



def query_file(file_path, category, attributes, id, language, text):
        data            = load_json_file(file_path)
        file_results    = {}

        for cat, attr_dict in data.items():
            if category is None or cat in category:
                for attr, id_dict in attr_dict.items():
                    if attributes is None or attr in attributes:
                        for id_val, lang_dict in id_dict.items():
                            if id is None or id_val in id:
                                filtered_lang_dict = filter_languages(lang_dict, language)
                                if filtered_lang_dict:
                                    if text is None or any(text in txt for txt in filtered_lang_dict.values()):
                                        if cat not in file_results:
                                            file_results[cat] = {}
                                        if attr not in file_results[cat]:
                                            file_results[cat][attr] = {}
                                        if id_val not in file_results[cat][attr]:
                                            file_results[cat][attr][id_val] = {}
                                        file_results[cat][attr][id_val].update(filtered_lang_dict)

        return file_results



def query_merged_data(file=None, category=None, attributes=None, id=None, language=None, text=None, save_results=False):
    results = {}

    if file == 'parsed_data' or file is None:
        file_path = os.path.join('parallel_corpus', 'parsed_data_merged.json')
        results.update(query_file(file_path, category, attributes, id, language, text))

    if file == 'unknown_resources' or file is None:
        file_path = os.path.join('parallel_corpus', 'unknown_resources_merged.json')
        results.update(query_file(file_path, category, attributes, id, language, text))

    return results



# loading...
data_file_path                      = os.path.join('parallel_corpus', 'parsed_data_merged.json')
data                                = load_json_file(data_file_path)
categories, attributes, languages   = extract_options_from_data(data)


# Streamlit pattern
st.sidebar.title("黑悟空多语言语料库")
st.sidebar.header("heiwukong multilingual corpus")

# Selection
file_type = st.sidebar.selectbox("💼 文件", ["parsed_data", "unknown_resources", "all"])
category = st.sidebar.multiselect("📁 类别（必选）category", categories)

# Process
if category:
    selected_attributes = set()
    for cat in category:
        selected_attributes.update(attributes.get(cat, []))
    attributes = st.sidebar.multiselect("💾 属性（必选）attributes", list(selected_attributes))
else:
    attributes = st.sidebar.multiselect("（属性）先选择类别", [])

language     = st.sidebar.multiselect("🗣 语言（必选）language", languages)
text         = st.sidebar.text_input("✍ 关键字（可选）keyword")
save_results = st.sidebar.checkbox("保存查询结果 save result")

# Retrieval
if st.sidebar.button("🔎 检索"):
    results = query_merged_data(
        file=file_type if file_type != "all" else None,
        category=category,
        attributes=attributes,
        id=None,  
        language=language,
        text=text,
        save_results=save_results
    )

    st.subheader("查询结果 🎯 RESULT")

    if save_results:
        json_data = json.dumps(results, ensure_ascii=False, indent=4)
        st.download_button(
            label="📥 下载查询结果",
            data=json_data,
            file_name="query_results.json",
            mime="application/json"
        )

    st.json(results)
