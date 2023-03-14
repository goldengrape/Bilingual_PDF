import fitz
import os
from utils import * 
import pdfkit 
# from tempfile import TemporaryDirectory
import argparse
from os import environ as env

def set_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--path", type=str, default="test_pdf", help="path to the pdf file")
    parser.add_argument("--filename", type=str, help="filename of the pdf file")
    parser.add_argument("--start_page", type=int, default=1, help="start page of the pdf file")
    parser.add_argument("--end_page", type=int, default=0, help="end page of the pdf file")
    parser.add_argument("--target_language", type=str, default="Chinese", help="target language of the pdf file")
    parser.add_argument("--htmltopdf", type=str, default=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe", help="path to the wkhtmltopdf")
    parser.add_argument("--openai_key", type=str, default="", help="OpenAI API KEY")
    args = parser.parse_args()
    return args

def process_book(
        source_doc,
        start_page,
        end_page,
        output_filename ,
        htmltopdf,
        target_language="Chinese",
        ):
    config=pdfkit.configuration(wkhtmltopdf=htmltopdf)
    total_page=end_page+1-start_page
    new_doc = fitz.open()

    # additional_convert_markdown_prompt="The text is from one page of a PDF file, and I will also give you part of the previous page and part of the next page of text. You can use the body parts of the previous and next pages to complete the text of the current page, as appropriate. You can remove the irrelevant information in the header and footer. However, you may not add anything that does not appear in the given text."
    # additional_convert_markdown_prompt="You can not add anything that does not appear in the given text."
    additional_convert_markdown_prompt=""
    additional_prompt="Note that the text is markdown, and the translation should not break its format, paying special attention to the beginning of the table. And do not add links to non-existent images."

    for page_number in range(start_page,end_page+1):
        print(f"Processing page {page_number+1}/{total_page+1}")
        # text=stitching_text(page_number,source_doc)
        text=source_doc[page_number].get_text()
        
        tmpdirname="tmp"
        if not os.path.exists(tmpdirname):
            os.makedirs(tmpdirname)

        insert_pdf_filename=process_one_page(text,
                        additional_convert_markdown_prompt=additional_convert_markdown_prompt,
                        additional_tranlate_prompt=additional_prompt,
                        target_language=target_language,
                        path=tmpdirname,
                        pdfkit_config=config)
        insert_doc=fitz.open(insert_pdf_filename)
        new_doc.insert_pdf(source_doc, from_page=page_number, to_page=page_number)
        for j in range(0,insert_doc.page_count):
            new_doc.insert_pdf(insert_doc, from_page=j, to_page=j)

        # 删除临时文件
        # 删除临时文件夹
        insert_doc.close()
        os.remove(insert_pdf_filename)
        os.removedirs(tmpdirname)
        new_doc.save(output_filename)
    new_doc.close()

if __name__ == "__main__":
    args=set_args()
    # path=args.path
    filename=args.filename
    # 按常人习惯，第一页是1，而不是0
    start_page=args.start_page-1
    end_page=args.end_page-1
    # 此处存在Prompt注入风险
    target_language=args.target_language

    htmltopdf=args.htmltopdf

    # source_doc = fitz.open(os.path.join(path,filename))
    source_doc = fitz.open(filename)
    if end_page<0:
        end_page=source_doc.page_count-1
    # output_filename=os.path.join(path, filename.replace(".pdf","_Bilingual.pdf"))
    
    output_filename=filename.replace(".pdf","_Bilingual.pdf")

    OPENAI_API_KEY = args.openai_key or env.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    process_book(source_doc,start_page,end_page,output_filename,htmltopdf,target_language)
