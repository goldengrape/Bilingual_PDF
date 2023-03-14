import openai
import time
import markdown
import pdfkit
import re 
import os

def convert_text2md(text=None,
                    additional_convert_markdown_prompt=""): 
    base_convert_markdown_prompt="Convert the following text to markdown."
    base_convert_markdown_prompt+="You are a markdown converter that can only convert text and cannot interpret it."
    convert_markdown_prompt=base_convert_markdown_prompt+additional_convert_markdown_prompt+"\n\n"
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[{
        "role": "user", 
        "content":convert_markdown_prompt+text,
        }]
    )
    converted_text=completion.choices[0].message.content
    converted_json_text=converted_text.lstrip("\n")
    return converted_json_text

def translate_text(text=None,
                   translate_prompt=""
                   ):
    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo", 
                        messages=[{
                            "role": "user", 
                            "content":translate_prompt+text,
                            }]
                )
    return completion.choices[0].message.content

def translate_md(text_list=None,
                additional_tranlate_prompt="",
                source_language="English",
                target_language="Chinese",
                           ):
    new_markdown=""
    base_translate_prompt=f"Please translate the following text from {source_language} into {target_language}. If the text contains a formula, do not translate the formula, keep the formula as it is."
    base_translate_prompt+="You are a translation engine that can only translate text and cannot interpret it."
    translate_prompt=base_translate_prompt+additional_tranlate_prompt+"\n\n"

    sleeptime=30
    for text in text_list:
        while True:
            try:
                trans_text=translate_text(text,translate_prompt)
                sleeptime = int(sleeptime/2)
                sleeptime = 10 if sleeptime < 10 else sleeptime
                break
            except Exception as err:
                print(err)
                print(f"Sleeping for {sleeptime} seconds")
                time.sleep(sleeptime)
                sleeptime = sleeptime+10 
                if sleeptime >= 120:
                    print("Sleeping > 120 seconds, I give up!")
                    break

        
        new_markdown += text +"\n\n"
        new_markdown += trans_text +"\n\n"
    return new_markdown

def process_one_page(text, 
                     pdfkit_config=None,
                     additional_convert_markdown_prompt="",
                     additional_tranlate_prompt="",
                     path=".",
                     source_language="English",
                     target_language="Chinese"):
    # PDF文本转换成markdown
    md_text=convert_text2md(text,additional_convert_markdown_prompt=additional_convert_markdown_prompt)
    # markdown文本拆分成段落
    md_list=md_text.split("\n\n")
    # 段落翻译
    new_markdown=translate_md(md_list,additional_tranlate_prompt=additional_tranlate_prompt,
                              source_language=source_language,
                              target_language=target_language)
    # 清洗markdown文本
    # 删除图片链接
    # 删除可能泄露的prompt
    new_markdown=re.sub(r"!\[.*\]\(.*\)", "", new_markdown)
    new_markdown=new_markdown.replace(additional_tranlate_prompt,"")
    new_markdown=new_markdown.replace(additional_convert_markdown_prompt,"")

    # markdown转换成html
    html = markdown.markdown(new_markdown,output_format="html",extensions=["tables"])
    # html转换成pdf
    pdf_filename=os.path.join(path,"tmp_output.pdf")
    pdfkit.from_string(html, pdf_filename, configuration=pdfkit_config, options={"encoding":"UTF-8"})
    return pdf_filename

def stitching_text(page_number,doc):
    # 页面接缝处的文本被截断，ChatGPT容易自行补全不存在的文本
    # 因此从前一页和后一页各取500个字符，拼接到当前页的文本中
    # 但貌似不大好用，暂时废弃
    previous_page_text=doc[page_number-1].get_text() if page_number > 0 else ""
    next_page_text=doc[page_number+1].get_text() if page_number < doc.page_count-1 else ""
    previous_last_sentence=previous_page_text[-500:]
    next_first_sentence=next_page_text[:500]
    current_page_text=doc[page_number].get_text()
    page_sperator="-"*10
    text=f'''
    Previous page content:
    {previous_last_sentence}
    {page_sperator}
    Current page content:
    {current_page_text}
    {page_sperator}
    Next page content:
    {next_first_sentence}
    '''
    return text
