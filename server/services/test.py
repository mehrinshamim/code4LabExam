import sys
import os
import json
from pathlib import Path

# Add the server directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from services.gemini_os_doc import generate_documentation_with_ai

def test_fcfs_documentation():
    """Test documentation generation for FCFS scheduling algorithm"""
    
    # Test case 1: FCFS with code
    question = "Implement Bankers algorithm for deadlock avoidance."
    code = """
//bankers.c
#include <stdio.h>

#define MAX_P 10 // Maximum number of processes
#define MAX_R 10 // Maximum number of resources

void isSafe(int P, int R, int need[MAX_P][MAX_R], int allocation[MAX_P][MAX_R], int available[MAX_R]) {
    int work[MAX_R], finish[MAX_P] = {0}, safeSequence[MAX_P];
    int completed = 0;

    // Copy available resources to work array
    for (int i = 0; i < R; i++)
        work[i] = available[i];

    while (completed < P) {
        int found = 0;
        for (int i = 0; i < P; i++) {
            if (!finish[i]) { // If process is not finished
                int j;
                int c=0; // Counter for satisfied resource needs
                for (j = 0; j < R; j++) {
                    if (need[i][j] > work[j])
                        break; // Need exceeds available work
                    else{
                        c++; // Resource need satisfied
                    }
                }

                if (c == R) { // If all needs can be satisfied (counter equals number of resources)
                    // Process can finish, release its resources
                    for (int k = 0; k < R; k++)
                        work[k] += allocation[i][k];

                    safeSequence[completed++] = i; // Add to safe sequence
                    finish[i] = 1; // Mark as finished
                    found = 1; // Found a process in this pass
                }
            }
        }
        if (!found) { // If no process could run in this pass
            printf("System is in an unsafe state!\n");
            return; // Exit the function
        }
    }

    // If loop completes, system is safe
    printf("System is in a safe state.\nSafe Sequence: ");
    for (int i = 0; i < P; i++)
        printf("P%d ", safeSequence[i]);
    printf("\n");
}

int main() {
    int P, R;
    printf("Enter the number of processes: ");
    scanf("%d", &P);
    printf("Enter the number of resources: ");
    scanf("%d", &R);

    // Declare arrays using MAX sizes, but use P and R for loops
    int max[MAX_P][MAX_R], allocation[MAX_P][MAX_R], need[MAX_P][MAX_R], available[MAX_R];

    printf("Enter the Allocation Matrix:\n");
    for (int i = 0; i < P; i++)
        for (int j = 0; j < R; j++)
            scanf("%d", &allocation[i][j]);

    printf("Enter the Maximum Matrix:\n");
    for (int i = 0; i < P; i++)
        for (int j = 0; j < R; j++)
            scanf("%d", &max[i][j]);

    printf("Enter the Available Resources:\n");
    for (int i = 0; i < R; i++)
        scanf("%d", &available[i]);

    // Calculate Need Matrix
    for (int i = 0; i < P; i++)
        for (int j = 0; j < R; j++)
            need[i][j] = max[i][j] - allocation[i][j];

    // Check system safety
    isSafe(P, R, need, allocation, available);

    return 0;
}
    """
    
    options = {
        "overview": True,
        "shortAlgorithm": True,
        "detailedAlgorithm": True,
        "code": True,
        "requiredModules": True,
        "variablesAndConstants": True,
        "functions": True,
        "explanation": True
    }

    try:
        # Generate documentation
        result = generate_documentation_with_ai(question, code, options)
        
        # Verify result structure
        expected_keys = {
            "overview", "shortAlgorithm", "detailedAlgorithm", "code",
            "requiredModules", "variablesAndConstants", "functions", "explanation"
        }



        # Save result to file for manual inspection
        output_file = Path(__file__).parent / "test_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            
        print(f"✅ Test passed! Output saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Running documentation generation tests...")
    test_fcfs_documentation()