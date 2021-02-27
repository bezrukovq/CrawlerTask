import edu.uci.ics.crawler4j.crawler.Page
import edu.uci.ics.crawler4j.crawler.WebCrawler
import edu.uci.ics.crawler4j.url.WebURL
import edu.uci.ics.crawler4j.parser.HtmlParseData
import java.io.PrintWriter
import java.io.IOException // Класс краулера
import java.util.ArrayList
import java.util.regex.Pattern

class HtmlCrawler : WebCrawler() {
    override fun shouldVisit(referringPage: Page, url: WebURL): Boolean {
        val urlString = url.url.toLowerCase()
        return (!EXCLUSIONS.matcher(urlString).matches()
                && urlString.contains("lostfilm-tv.ru/"))
    }

    override fun visit(page: Page) {
        val url = page.webURL.url
        if (page.parseData is HtmlParseData) {
            val htmlParseData = page.parseData as HtmlParseData
            val html = htmlParseData.html
            count++
            try {
                val writer = PrintWriter("src/pages/" + count + ".txt", "UTF-8")
                writer.println(html)
                writer.close()
                urlList.add(url)
            } catch (e: IOException) {
                e.printStackTrace()
            }
        }
    }

    companion object {
        private val EXCLUSIONS = Pattern.compile(".*(\\.(css|js|xml|gif|jpg|png|mp3|mp4|zip|gz|pdf))$")
        var count = 0
        var urlList = ArrayList<String>()
    }
}