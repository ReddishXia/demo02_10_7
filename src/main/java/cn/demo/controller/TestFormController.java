//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package cn.demo.controller;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;


@CrossOrigin
@Controller
public class TestFormController {
    public TestFormController() {
    }

    @GetMapping({"/"})
    public String toIndex() {
        return "main.html";
    }

    @RequestMapping({"/input"})
    public String input() {
        return "index.html";
    }

    public static boolean isWindows() {
        return System.getProperty("os.name").toUpperCase().indexOf("WINDOWS") >= 0;
    }

    public static void testMethod1(String num) throws IOException, InterruptedException {
        System.out.println("isProcess");
        String PATH = "";
        String[] args1 = new String[]{"C:\\Users\\79988\\anaconda3\\envs\\py39\\python.exe", "./src/main/resources/static/getDB.py", num, " "};
        new ProcessBuilder(new String[]{"C:\\Users\\79988\\anaconda3\\envs\\py39\\python.exe", PATH});
        Process proc;
        BufferedReader in;
        String line;
        if (isWindows()) {
            System.out.println(num);
            proc = Runtime.getRuntime().exec(args1);
            in = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            line = null;

            while((line = in.readLine()) != null) {
                System.out.println(line);
            }

            in.close();
        } else {
            args1 = new String[]{"/root/anaconda3/envs/py39/bin/python", "/root/getDB.py", num, " "};
//            System.out.println("isProcess");
            proc = Runtime.getRuntime().exec(args1);
            in = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            line = null;

            while((line = in.readLine()) != null) {
                System.out.println(line);
            }

            in.close();
        }

    }

    @RequestMapping({"/submit"})
    public String index(@RequestParam("num") int num, Model model, HttpServletResponse response, HttpServletRequest request) throws IOException, InterruptedException {
        String path = "";
        if (isWindows()) {
            path = "./src/main/resources/templates/";
        } else {
            path = "/root/picture/";
        }

        int judge = 0;
        String[] fileNameList = new String[4];
        File desktop = new File(path);
        String[] arr = desktop.list();
        String[] var10 = arr;
        int var11 = arr.length;

        for(int var12 = 0; var12 < var11; ++var12) {
            String string = var10[var12];
            if (string.endsWith(num + ".png")) {
                fileNameList[judge] = string;
                System.out.println(string);
                ++judge;
            }
        }

        if (judge == 0) {
            System.out.println("python");
            testMethod1(String.valueOf(num));
            File desktopNew = new File(path);
            String[] arrNew = desktopNew.list();
            String[] var18 = arrNew;
            int var19 = arrNew.length;

            for(int var14 = 0; var14 < var19; ++var14) {
                String string = var18[var14];
                if (string.endsWith(num + ".png")) {
                    fileNameList[judge] = string;
                    ++judge;
                }
            }
        }

        if (judge == 0) {
            return "error.html";
        } else {
            if (isWindows()) {
                new File("./");
                model.addAttribute("imageurl", "./" + fileNameList[3]);
                System.out.println(fileNameList[3]);
                model.addAttribute("imageurl1", "./" + fileNameList[0]);
                System.out.println(fileNameList[2]);
                model.addAttribute("imageurl2", "./" + fileNameList[2]);
                System.out.println(fileNameList[1]);
                model.addAttribute("imageurl3", "./" + fileNameList[1]);
                System.out.println(fileNameList[0]);
            } else {
                model.addAttribute("imageurl", "../../../../../picture/" + fileNameList[3]);
                model.addAttribute("imageurl1", "../../../../../picture/" + fileNameList[0]);
                model.addAttribute("imageurl2", "../../../../../picture/" + fileNameList[2]);
                model.addAttribute("imageurl3", "../../../../../picture/" + fileNameList[1]);
            }

            return "test.html";
        }
    }
}
