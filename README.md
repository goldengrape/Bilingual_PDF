# Bilingual_PDF

您需提前安装wkhtmltopdf:
https://wkhtmltopdf.org/downloads.html
记住wkhtmltopdf运行文件的位置，如果是windows默认安装，通常就是
`C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`
## 使用

```
python main.py --filename test_pdf\Atchison2006.pdf --start_page 1 --end_page 3 --target_language Chinese
```
如果是其他系统下或没有将wkhtmltopdf安装在默认位置，可能需要指定htmltopdf可执行文件的位置
```
python main.py --filename test_pdf\Atchison2006.pdf --start_page 1 --end_page 3 --target_language Chinese --htmltopdf "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
```
## 警告

1. 注意ChatGPT的翻译并不可靠！甚至，在页面起始和结尾处有可能它自行发挥，增加不存在的文本。
2. 翻译质量不稳定。
3. 特别特别慢，一页大概需要3分钟时间。
