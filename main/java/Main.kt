import kotlin.Throws
import kotlin.jvm.JvmStatic
import java.io.File
import edu.uci.ics.crawler4j.crawler.CrawlConfig
import edu.uci.ics.crawler4j.robotstxt.RobotstxtConfig
import edu.uci.ics.crawler4j.robotstxt.RobotstxtServer
import edu.uci.ics.crawler4j.crawler.CrawlController
import edu.uci.ics.crawler4j.crawler.CrawlController.WebCrawlerFactory
import edu.uci.ics.crawler4j.fetcher.PageFetcher
import java.io.PrintWriter
import java.lang.Exception

object Main {
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
        val crawlStorage = File("src/test/resources/crawler4j")
        val config = CrawlConfig()
        config.maxPagesToFetch = 120
        config.crawlStorageFolder = crawlStorage.absolutePath
        val numCrawlers = 12
        val pageFetcher = PageFetcher(config)
        val robotstxtConfig = RobotstxtConfig()
        val robotstxtServer = RobotstxtServer(robotstxtConfig, pageFetcher)
        val controller = CrawlController(config, pageFetcher, robotstxtServer)
        controller.addSeed("https://lostfilm-tv.ru/")
        val factory = WebCrawlerFactory { HtmlCrawler() }
        controller.start(factory, numCrawlers)
        val writer = PrintWriter("src/pages/index.txt" + "", "UTF-8")
        var index = 1
        for (s in HtmlCrawler.urlList) {
            writer.println("$index -> $s")
            index++
        }
        writer.close()
    }
}