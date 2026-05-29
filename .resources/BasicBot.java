import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Random;

public class BasicBot {

    private static record Item(int id, int size, int weight, int value) { }

    public static void main(String[] args) {

        Random rng = new Random();
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

        try {
            String[] strs = reader.readLine().split(" ");
            assert strs[0].equals("n_items") && strs.length == 2;
            int nItems = Integer.parseInt(strs[1]);

            strs = reader.readLine().split(" ");
            assert strs[0].equals("size_capacity") && strs.length == 2;
            int sizeCapacity = Integer.parseInt(strs[1]);

            strs = reader.readLine().split(" ");
            assert strs[0].equals("weight_capacity") && strs.length == 2;
            int weightCapacity = Integer.parseInt(strs[1]);

            Item[] items = new Item[nItems];

            for (int i = 0; i < nItems; i++) {
                strs = reader.readLine().split(" ");
                assert strs.length == 4;
                items[i] = new Item(Integer.parseInt(strs[0]), Integer.parseInt(strs[1]), Integer.parseInt(strs[2]), Integer.parseInt(strs[3]));
            }

            strs = reader.readLine().split(" ");
            assert strs[0].equals("preprocessing") && strs.length == 2;
            int preprocessingTime = Integer.parseInt(strs[1]);

            // calculs préliminaires
            

            while (true) {
                strs = reader.readLine().split(" ");
                assert strs[0].equals("taken") && strs.length == 2;
                int taken = Integer.parseInt(strs[1]);

                // mise à jour des informations sur les objets disponibles

                strs = reader.readLine().split(" ");
                assert strs[0].equals("next_item") && strs.length == 2;
                int processingTime = Integer.parseInt(strs[1]);

                System.out.println(rng.nextInt(nItems));
            }
            
        } catch (IOException e) {
            System.err.println(e);
        } finally {
            try {
                reader.close();
            } catch (IOException e) {
                System.err.println(e);
            }
        }
    }
    
}
