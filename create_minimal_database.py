#!/usr/bin/env python3
"""
Create a minimal vector database for testing O-RAN × Nephio RAG system
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_minimal_database():
    """Create a minimal database with sample documents"""
    print("[*] Creating minimal vector database for testing...")
    
    try:
        from oran_nephio_rag import VectorDatabaseManager
        from config import Config
        from langchain.docstore.document import Document
        
        # Initialize components
        config = Config()
        vector_manager = VectorDatabaseManager(config)
        
        # Create sample documents about O-RAN and Nephio
        sample_docs = [
            Document(
                page_content="""
                Nephio is an open-source project that provides a Kubernetes-based automation platform 
                for deploying and managing cloud-native Network Functions (CNFs). It focuses on 
                simplifying the lifecycle management of network functions through GitOps principles 
                and declarative configuration management.
                """,
                metadata={
                    "source": "nephio-overview",
                    "type": "documentation",
                    "description": "Nephio Overview"
                }
            ),
            Document(
                page_content="""
                O-RAN (Open Radio Access Network) is an initiative to create open and intelligent 
                radio access networks. It promotes disaggregation of hardware and software, 
                standardized interfaces, and AI/ML-driven optimization. O-RAN enables multi-vendor 
                interoperability and innovation in 5G networks.
                """,
                metadata={
                    "source": "oran-overview",
                    "type": "documentation", 
                    "description": "O-RAN Overview"
                }
            ),
            Document(
                page_content="""
                Network Function Scale-out refers to the process of increasing the capacity of 
                network functions by adding more instances or resources. In Nephio, this is 
                achieved through Kubernetes horizontal pod autoscaling and custom resource 
                definitions that manage the lifecycle of network function deployments.
                """,
                metadata={
                    "source": "scale-out-guide",
                    "type": "documentation",
                    "description": "Network Function Scale-out Guide"
                }
            ),
            Document(
                page_content="""
                Scale-in is the opposite of scale-out, involving the reduction of network function 
                instances when demand decreases. Nephio provides automated scale-in capabilities 
                through monitoring metrics and policy-based decisions to optimize resource utilization 
                while maintaining service quality.
                """,
                metadata={
                    "source": "scale-in-guide", 
                    "type": "documentation",
                    "description": "Network Function Scale-in Guide"
                }
            ),
            Document(
                page_content="""
                The integration between O-RAN and Nephio enables automated deployment and management 
                of O-RAN components such as O-DU (Distributed Unit), O-CU (Central Unit), and 
                O-RIC (RAN Intelligent Controller). This integration supports dynamic scaling 
                based on network conditions and traffic patterns.
                """,
                metadata={
                    "source": "oran-nephio-integration",
                    "type": "documentation",
                    "description": "O-RAN Nephio Integration"
                }
            )
        ]
        
        print(f"[+] Created {len(sample_docs)} sample documents")
        
        # Build vector database
        print("[*] Building vector database...")
        success = vector_manager.build_vector_database(sample_docs)
        
        if success:
            print("[+] Minimal vector database created successfully!")
            
            # Test loading
            print("[*] Testing database loading...")
            if vector_manager.load_existing_database():
                print("[+] Database loading successful!")
                
                # Test similarity search
                print("[*] Testing similarity search...")
                results = vector_manager.search_similar("What is Nephio?", k=2)
                print(f"[+] Found {len(results)} similar documents")
                
                for i, (doc, score) in enumerate(results, 1):
                    print(f"   {i}. {doc.metadata.get('description', 'Unknown')}")
                
                return True
            else:
                print("[-] Database loading failed")
                return False
        else:
            print("[-] Database creation failed")
            return False
            
    except Exception as e:
        print(f"[-] Failed to create minimal database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("O-RAN x Nephio RAG System - Minimal Database Creator")
    print("=" * 60)
    
    success = create_minimal_database()
    
    print("\n" + "=" * 60)
    if success:
        print("[+] Minimal database ready!")
        print("\nYou can now test the system:")
        print("1. Run: python main.py")
        print("2. Try asking questions like:")
        print("   - What is Nephio?")
        print("   - How does O-RAN work?")
        print("   - What is network function scale-out?")
    else:
        print("[-] Failed to create minimal database")
    print("=" * 60)