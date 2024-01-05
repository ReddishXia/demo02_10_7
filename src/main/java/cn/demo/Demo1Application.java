//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//
package cn.demo;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.CrossOrigin;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

@CrossOrigin
@SpringBootApplication
public class Demo1Application {
    public Demo1Application() {
    }

    public static boolean isWindows() {
        return System.getProperty("os.name").toUpperCase().indexOf("WINDOWS") >= 0;
    }

    public static void testMethod1() throws IOException, InterruptedException {
        System.out.println("fsdfsdfsdf");
        String PATH = "";
        String[] args1 = new String[]{"C:\\Users\\79988\\anaconda3\\envs\\py39\\python.exe", "E:\\test.py", "7824075", " "};
        new ProcessBuilder(new String[]{"C:\\Users\\79988\\anaconda3\\envs\\py39\\python.exe", PATH});
        if (isWindows()) {
            System.out.println("fsdfsdfsdf");
            Process proc = Runtime.getRuntime().exec(args1);
            BufferedReader in = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            String line = null;

            while((line = in.readLine()) != null) {
                System.out.println(line);
            }

            in.close();
        } else {
            PATH = "/root/test.py";
            new ProcessBuilder(new String[]{"/root/anaconda3/envs/py39/bin/python", PATH});
        }

    }

    public static void main(String[] args) throws IOException, InterruptedException {
        SpringApplication.run(Demo1Application.class, args);
    }
}
