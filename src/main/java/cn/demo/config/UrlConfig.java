//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package cn.demo.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class UrlConfig implements WebMvcConfigurer {
    public UrlConfig() {
    }

    public static boolean isWindows() {
        return System.getProperty("os.name").toUpperCase().indexOf("WINDOWS") >= 0;
    }

    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        if (!isWindows()) {
            registry.addResourceHandler(new String[]{"/**"}).addResourceLocations(new String[]{"file:/root/picture"});
        }

        if (isWindows()) {
            registry.addResourceHandler(new String[]{"/**"}).addResourceLocations(new String[]{"classpath:/templates/"});
        }

    }
}
