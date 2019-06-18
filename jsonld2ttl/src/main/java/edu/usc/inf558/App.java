package edu.usc.inf558;

import org.apache.jena.rdf.model.*;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args ) throws FileNotFoundException
    {
        /*
        command to run : java -cp target/jsonld2ttl-1.0-SNAPSHOT.jar edu.usc.inf558.App data/allrecipes.jsonld allrecipes.ttl
         */
        Model model = ModelFactory.createDefaultModel();
        model.read(args[0]);
        //model.write(System.out,"TURTLE");
        OutputStream out = new FileOutputStream(args[1]);
        model.write(out,"TURTLE");
        int i = 0;
        String prev = null;
        StmtIterator iter = model.listStatements();
        while (iter.hasNext()) {
            Statement stmt = iter.nextStatement();
            Resource subject = stmt.getSubject();
            if (prev == null){
                prev = subject.toString();
            }
            if (prev.equals(subject.toString())){
                i += 1;
            }
            else {
                System.out.print(prev+"  property: "+ i +"\n");
                prev = subject.toString();
                i = 1;
            }
        }
        System.out.print(prev + " property: " + i);

    }
}
