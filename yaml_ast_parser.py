# ============================================================================
# The base of this YAML to AST parser was vibe coded using Claude Sonnet 4.5
# ============================================================================

import yaml
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union
from enum import Enum
from abc import ABC, abstractmethod


# ============================================================================
# AST Node Types - Representing YAML Grammar
# ============================================================================

class ASTNode(ABC):
    """Base class for all AST nodes"""
    
    @abstractmethod
    def __repr__(self, indent=0):
        pass


@dataclass
class ScalarNode(ASTNode):
    """Represents a scalar value (string, number, boolean, null)"""
    value: Any
    tag: Optional[str] = None
    style: Optional[str] = None
    start_mark: Optional[tuple] = None  # (line, column)
    end_mark: Optional[tuple] = None
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        type_info = f" ({type(self.value).__name__})" if self.value is not None else ""
        mark_info = f" @{self.start_mark}" if self.start_mark else ""
        return f"{spaces}ScalarNode{type_info}: {repr(self.value)}{mark_info}"


@dataclass
class SequenceNode(ASTNode):
    """Represents a YAML sequence (list/array)"""
    elements: List[ASTNode] = field(default_factory=list)
    tag: Optional[str] = None
    flow_style: bool = False
    start_mark: Optional[tuple] = None
    end_mark: Optional[tuple] = None
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        style = " [flow]" if self.flow_style else ""
        mark_info = f" @{self.start_mark}" if self.start_mark else ""
        result = f"{spaces}SequenceNode{style}{mark_info}"
        if self.elements:
            result += "\n" + "\n".join(elem.__repr__(indent + 1) for elem in self.elements)
        return result


@dataclass
class MappingNode(ASTNode):
    """Represents a YAML mapping (dictionary/object)"""
    pairs: List['KeyValuePair'] = field(default_factory=list)
    tag: Optional[str] = None
    flow_style: bool = False
    start_mark: Optional[tuple] = None
    end_mark: Optional[tuple] = None
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        style = " {flow}" if self.flow_style else ""
        mark_info = f" @{self.start_mark}" if self.start_mark else ""
        result = f"{spaces}MappingNode{style}{mark_info}"
        if self.pairs:
            result += "\n" + "\n".join(pair.__repr__(indent + 1) for pair in self.pairs)
        return result


@dataclass
class KeyValuePair(ASTNode):
    """Represents a key-value pair in a mapping"""
    key: ASTNode
    value: ASTNode
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        result = f"{spaces}KeyValuePair"
        result += f"\n{spaces}  key:\n{self.key.__repr__(indent + 2)}"
        result += f"\n{spaces}  value:\n{self.value.__repr__(indent + 2)}"
        return result


@dataclass
class DocumentNode(ASTNode):
    """Represents a YAML document (root node)"""
    root: Optional[ASTNode] = None
    version: Optional[tuple] = None  # e.g., (1, 2) for YAML 1.2
    tags: Optional[dict] = None
    explicit_start: bool = False
    explicit_end: bool = False
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        version_info = f" v{self.version}" if self.version else ""
        result = f"{spaces}DocumentNode{version_info}"
        if self.root:
            result += "\n" + self.root.__repr__(indent + 1)
        return result


@dataclass
class StreamNode(ASTNode):
    """Represents a YAML stream (can contain multiple documents)"""
    documents: List[DocumentNode] = field(default_factory=list)
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        result = f"{spaces}StreamNode ({len(self.documents)} document(s))"
        if self.documents:
            result += "\n" + "\n".join(doc.__repr__(indent + 1) for doc in self.documents)
        return result


@dataclass
class AliasNode(ASTNode):
    """Represents a YAML alias (reference to an anchor)"""
    anchor: str
    start_mark: Optional[tuple] = None
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        return f"{spaces}AliasNode: *{self.anchor}"


@dataclass
class AnchorNode(ASTNode):
    """Represents a YAML anchor (defines a reusable node)"""
    anchor: str
    node: ASTNode
    
    def __repr__(self, indent=0):
        spaces = "  " * indent
        result = f"{spaces}AnchorNode: &{self.anchor}"
        result += "\n" + self.node.__repr__(indent + 1)
        return result


# ============================================================================
# YAML AST Parser - Converts YAML to proper AST
# ============================================================================

class YAMLASTParser:
    """Parser that converts YAML to a proper Abstract Syntax Tree"""
    
    def __init__(self):
        self.anchors = {}  # Store anchors for alias resolution
    
    def parse_file(self, filepath: str) -> StreamNode:
        """Parse a YAML file and return the AST"""
        with open(filepath, 'r') as f:
            return self.parse_string(f.read())
    
    def parse_string(self, yaml_string: str) -> StreamNode:
        """Parse a YAML string and return the AST"""
        stream = StreamNode()
        
        # Use yaml.compose_all to get the raw node structure with position info
        for yaml_node in yaml.compose_all(yaml_string):
            self.anchors = {}  # Reset anchors for each document
            doc = DocumentNode()
            
            if yaml_node:
                doc.root = self._build_ast(yaml_node)
            
            stream.documents.append(doc)
        
        return stream
    
    def _get_mark(self, yaml_node) -> Optional[tuple]:
        """Extract position information from YAML node"""
        if hasattr(yaml_node, 'start_mark') and yaml_node.start_mark:
            return (yaml_node.start_mark.line, yaml_node.start_mark.column)
        return None
    
    def _build_ast(self, yaml_node) -> ASTNode:
        """Recursively build AST from PyYAML's node structure"""
        
        # Handle anchors
        if hasattr(yaml_node, 'anchor') and yaml_node.anchor:
            node = self._build_ast_node(yaml_node)
            anchor_node = AnchorNode(anchor=yaml_node.anchor, node=node)
            self.anchors[yaml_node.anchor] = anchor_node
            return anchor_node
        
        return self._build_ast_node(yaml_node)
    
    def _build_ast_node(self, yaml_node) -> ASTNode:
        """Build AST node based on YAML node type"""
        
        # Scalar nodes
        if isinstance(yaml_node, yaml.ScalarNode):
            # Convert string representation to actual Python type
            value = yaml_node.value
            
            # Try to infer the actual type
            if yaml_node.tag == 'tag:yaml.org,2002:null' or value in ('null', 'Null', 'NULL', '~', ''):
                value = None
            elif yaml_node.tag == 'tag:yaml.org,2002:bool':
                value = value.lower() in ('true', 'yes', 'on')
            elif yaml_node.tag == 'tag:yaml.org,2002:int':
                value = int(value)
            elif yaml_node.tag == 'tag:yaml.org,2002:float':
                value = float(value)
            # For strings and other types, keep as-is
            
            return ScalarNode(
                value=value,
                tag=yaml_node.tag,
                style=yaml_node.style,
                start_mark=self._get_mark(yaml_node)
            )
        
        # Sequence nodes
        elif isinstance(yaml_node, yaml.SequenceNode):
            elements = [self._build_ast(item) for item in yaml_node.value]
            return SequenceNode(
                elements=elements,
                tag=yaml_node.tag,
                flow_style=(yaml_node.flow_style == True),
                start_mark=self._get_mark(yaml_node)
            )
        
        # Mapping nodes
        elif isinstance(yaml_node, yaml.MappingNode):
            pairs = []
            for key_node, value_node in yaml_node.value:
                key_ast = self._build_ast(key_node)
                value_ast = self._build_ast(value_node)
                pairs.append(KeyValuePair(key=key_ast, value=value_ast))
            
            return MappingNode(
                pairs=pairs,
                tag=yaml_node.tag,
                flow_style=(yaml_node.flow_style == True),
                start_mark=self._get_mark(yaml_node)
            )
        
        # Unknown node type
        else:
            raise ValueError(f"Unknown YAML node type: {type(yaml_node)}")
    
    def traverse(self, node: ASTNode, callback):
        """Traverse the AST and call callback on each node"""
        callback(node)
        
        if isinstance(node, StreamNode):
            for doc in node.documents:
                self.traverse(doc, callback)
        elif isinstance(node, DocumentNode):
            if node.root:
                self.traverse(node.root, callback)
        elif isinstance(node, SequenceNode):
            for elem in node.elements:
                self.traverse(elem, callback)
        elif isinstance(node, MappingNode):
            for pair in node.pairs:
                self.traverse(pair, callback)
        elif isinstance(node, KeyValuePair):
            self.traverse(node.key, callback)
            self.traverse(node.value, callback)
        elif isinstance(node, AnchorNode):
            self.traverse(node.node, callback)


# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    """Main function for command-line usage"""
    import argparse
    import sys
    
    # Set up argument parser
    parser_cli = argparse.ArgumentParser(
        description='Parse YAML files and generate an Abstract Syntax Tree',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a YAML file and show the AST
  python yaml_ast_parser.py config.yaml
  
  # Show detailed analysis
  python yaml_ast_parser.py config.yaml --analyze
  
  # Show only the tree structure
  python yaml_ast_parser.py config.yaml --tree-only
  
  # Parse from stdin
  cat config.yaml | python yaml_ast_parser.py -
        """
    )
    
    parser_cli.add_argument(
        'file',
        help='YAML file to parse (use "-" for stdin)'
    )
    
    parser_cli.add_argument(
        '-a', '--analyze',
        action='store_true',
        help='Show detailed analysis of the AST'
    )
    
    parser_cli.add_argument(
        '-t', '--tree-only',
        action='store_true',
        help='Show only the tree structure without analysis'
    )
    
    parser_cli.add_argument(
        '-k', '--keys',
        action='store_true',
        help='List all mapping keys'
    )
    
    parser_cli.add_argument(
        '-v', '--values',
        action='store_true',
        help='List all scalar values'
    )
    
    args = parser_cli.parse_args()
    
    # Create parser instance
    yaml_parser = YAMLASTParser()
    
    try:
        # Parse input
        if args.file == '-':
            # Read from stdin
            yaml_content = sys.stdin.read()
            ast = yaml_parser.parse_string(yaml_content)
        else:
            # Read from file
            ast = yaml_parser.parse_file(args.file)
        
        # Display AST
        if not args.tree_only:
            print("YAML Abstract Syntax Tree:")
            print("=" * 70)
        print(ast)
        
        # Show analysis if requested
        if args.analyze or args.keys or args.values:
            print("\n" + "=" * 70)
            print("AST Analysis:")
            print("=" * 70)
            
            # Count different node types
            if args.analyze:
                node_counts = {}
                def count_nodes(node):
                    node_type = type(node).__name__
                    node_counts[node_type] = node_counts.get(node_type, 0) + 1
                
                yaml_parser.traverse(ast, count_nodes)
                
                print("\nNode type distribution:")
                for node_type, count in sorted(node_counts.items()):
                    print(f"  {node_type}: {count}")
            
            # Extract all keys from mappings
            if args.keys or args.analyze:
                print("\nAll mapping keys:")
                def print_keys(node):
                    if isinstance(node, KeyValuePair):
                        if isinstance(node.key, ScalarNode):
                            print(f"  - {node.key.value}")
                
                yaml_parser.traverse(ast, print_keys)
            
            # Find all scalar values
            if args.values or args.analyze:
                print("\nAll scalar values:")
                def print_scalars(node):
                    if isinstance(node, ScalarNode):
                        value_type = type(node.value).__name__
                        print(f"  - {node.value} ({value_type})")
                
                yaml_parser.traverse(ast, print_scalars)
        
        return 0
        
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        return 1
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # If command-line arguments provided, use CLI mode
    if len(sys.argv) > 1:
        sys.exit(main())
    
    # Otherwise, run example
    print("Running example (use --help for command-line options)")
    print()
    
    yaml_content = """
name: MyProject
version: 1.0.0
dependencies:
  - name: requests
    version: 2.28.0
  - name: pyyaml
    version: 6.0
config:
  debug: true
  max_connections: 100
  timeout: 30.5
  servers:
    primary: server1.example.com
    backup: server2.example.com
  features: [auth, logging, caching]
"""
    
    # Parse the YAML
    parser = YAMLASTParser()
    ast = parser.parse_string(yaml_content)
    
    # Print the AST
    print("YAML Abstract Syntax Tree:")
    print("=" * 70)
    print(ast)
    
    print("\n" + "=" * 70)
    print("AST Analysis:")
    print("=" * 70)
    
    # Count different node types
    node_counts = {}
    def count_nodes(node):
        node_type = type(node).__name__
        node_counts[node_type] = node_counts.get(node_type, 0) + 1
    
    parser.traverse(ast, count_nodes)
    
    print("\nNode type distribution:")
    for node_type, count in sorted(node_counts.items()):
        print(f"  {node_type}: {count}")
    
    # Extract all keys from mappings
    print("\nAll mapping keys:")
    def print_keys(node):
        if isinstance(node, KeyValuePair):
            if isinstance(node.key, ScalarNode):
                print(f"  - {node.key.value}")
    
    parser.traverse(ast, print_keys)
    
    # Find all numeric values
    print("\nAll numeric values:")
    def print_numbers(node):
        if isinstance(node, ScalarNode):
            if isinstance(node.value, (int, float)):
                print(f"  - {node.value} (type: {type(node.value).__name__})")
    
    parser.traverse(ast, print_numbers)
